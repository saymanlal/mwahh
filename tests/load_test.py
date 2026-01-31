#!/usr/bin/env python3
"""
Load testing script for the matchmaking platform.

Usage:
    python load_test.py --host http://localhost:8000 --users 100 --duration 60
"""

import asyncio
import random
import string
import time
import argparse
from typing import List, Tuple
import statistics

import aiohttp
import websockets
import json

class LoadTest:
    def __init__(self, host: str, num_users: int, duration: int):
        self.host = host.rstrip('/')
        self.num_users = num_users
        self.duration = duration
        self.api_url = f"{self.host}/api"
        self.ws_url = f"{self.host.replace('http', 'ws')}/ws"
        
        self.results = {
            'registration': [],
            'authentication': [],
            'matching': [],
            'messages': [],
            'errors': 0,
        }

    @staticmethod
    def _random_email():
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return f"{random_id}@test.college.edu"

    @staticmethod
    def _random_handle():
        adjectives = ['swift', 'bold', 'calm', 'eager']
        animals = ['tiger', 'eagle', 'wolf', 'puma']
        return f"{random.choice(adjectives)}_{random.choice(animals)}{random.randint(1000, 9999)}"

    async def register_user(self, session: aiohttp.ClientSession) -> Tuple[str, str, str]:
        """Register a new user and return (email, password, handle)"""
        email = self._random_email()
        password = "TestPassword123!"
        
        try:
            async with session.post(
                f"{self.api_url}/auth/register/",
                json={"email": email, "password": password},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                start = time.time()
                data = await resp.json()
                elapsed = time.time() - start
                
                if resp.status == 201:
                    self.results['registration'].append(elapsed)
                    return email, password, None
                else:
                    self.results['errors'] += 1
                    return None, None, None
        except Exception as e:
            print(f"Registration error: {e}")
            self.results['errors'] += 1
            return None, None, None

    async def verify_and_authenticate(self, session: aiohttp.ClientSession, email: str, password: str) -> Tuple[str, str]:
        """Verify OTP and get auth tokens (uses dummy OTP 000000)"""
        try:
            start = time.time()
            async with session.post(
                f"{self.api_url}/auth/verify-otp/",
                json={"email": email, "otp": "000000"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                elapsed = time.time() - start
                
                if resp.status == 200:
                    data = await resp.json()
                    self.results['authentication'].append(elapsed)
                    return data['access'], data['user']['user_uuid']
                else:
                    self.results['errors'] += 1
                    return None, None
        except Exception as e:
            print(f"Auth error: {e}")
            self.results['errors'] += 1
            return None, None

    async def find_matches(self, session: aiohttp.ClientSession, access_token: str):
        """Find matches"""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            start = time.time()
            
            async with session.get(
                f"{self.api_url}/matching/",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                elapsed = time.time() - start
                
                if resp.status == 200:
                    data = await resp.json()
                    self.results['matching'].append(elapsed)
                    return data
                else:
                    self.results['errors'] += 1
                    return []
        except Exception as e:
            print(f"Matching error: {e}")
            self.results['errors'] += 1
            return []

    async def create_match(self, session: aiohttp.ClientSession, access_token: str, target_uuid: str):
        """Create a match with a target user"""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            async with session.post(
                f"{self.api_url}/matching/create_match/",
                headers=headers,
                json={"target_user_id": target_uuid, "mode": "friend"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status in [200, 201]:
                    return await resp.json()
                else:
                    self.results['errors'] += 1
                    return None
        except Exception as e:
            self.results['errors'] += 1
            return None

    async def send_message_ws(self, room_id: str, access_token: str):
        """Send a message via WebSocket"""
        try:
            ws_url = f"{self.ws_url}/chat/{room_id}/?token={access_token}"
            
            async with websockets.connect(ws_url, ping_interval=None) as websocket:
                start = time.time()
                
                await websocket.send(json.dumps({
                    "type": "message",
                    "message_type": "text",
                    "content": "Load test message"
                }))
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                elapsed = time.time() - start
                
                if response:
                    self.results['messages'].append(elapsed)
        except Exception as e:
            self.results['errors'] += 1

    async def run_user_session(self, session: aiohttp.ClientSession):
        """Simulate a single user's session"""
        # Register
        email, password, _ = await self.register_user(session)
        if not email:
            return

        # Authenticate
        access_token, user_uuid = await self.verify_and_authenticate(session, email, password)
        if not access_token:
            return

        # Find matches
        matches = await self.find_matches(session, access_token)
        if not matches:
            return

        # Create match with first candidate if available
        if matches and len(matches) > 0:
            first_match = matches[0]
            target_uuid = first_match.get('user_a_handle') if first_match else None
            if target_uuid:
                match_result = await self.create_match(session, access_token, target_uuid)
                
                if match_result:
                    room_id = match_result.get('chat_room')
                    if room_id:
                        await self.send_message_ws(room_id, access_token)

    async def run_load_test(self):
        """Run the load test"""
        print(f"Starting load test: {self.num_users} users for {self.duration}s")
        print(f"Target: {self.host}")
        print()

        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            while time.time() - start_time < self.duration:
                if len(tasks) < self.num_users:
                    task = asyncio.create_task(self.run_user_session(session))
                    tasks.append(task)
                
                completed, tasks = await asyncio.wait(
                    tasks,
                    timeout=0.5,
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in completed:
                    try:
                        await task
                    except Exception as e:
                        print(f"Task error: {e}")
            
            # Wait for remaining tasks
            if tasks:
                await asyncio.wait(tasks)

        self._print_results()

    def _print_results(self):
        """Print test results"""
        print("\n" + "="*60)
        print("LOAD TEST RESULTS")
        print("="*60)

        def print_stats(name: str, times: List[float]):
            if not times:
                print(f"\n{name}: No data collected")
                return
            
            print(f"\n{name}:")
            print(f"  Count: {len(times)}")
            print(f"  Min: {min(times):.3f}s")
            print(f"  Max: {max(times):.3f}s")
            print(f"  Avg: {statistics.mean(times):.3f}s")
            if len(times) > 1:
                print(f"  StdDev: {statistics.stdev(times):.3f}s")
            print(f"  p50: {sorted(times)[len(times)//2]:.3f}s")
            if len(times) >= 20:
                print(f"  p95: {sorted(times)[int(len(times)*0.95)]:.3f}s")
                print(f"  p99: {sorted(times)[int(len(times)*0.99)]:.3f}s")

        print_stats("Registration", self.results['registration'])
        print_stats("Authentication", self.results['authentication'])
        print_stats("Matching", self.results['matching'])
        print_stats("Messages", self.results['messages'])

        print(f"\nTotal Errors: {self.results['errors']}")
        total_requests = (
            len(self.results['registration']) +
            len(self.results['authentication']) +
            len(self.results['matching']) +
            len(self.results['messages'])
        )
        print(f"Total Requests: {total_requests}")
        
        if total_requests > 0:
            error_rate = (self.results['errors'] / (total_requests + self.results['errors'])) * 100
            print(f"Error Rate: {error_rate:.2f}%")


def main():
    parser = argparse.ArgumentParser(description='Load test the matchmaking platform')
    parser.add_argument('--host', default='http://localhost:8000', help='API host URL')
    parser.add_argument('--users', type=int, default=10, help='Number of concurrent users')
    parser.add_argument('--duration', type=int, default=30, help='Test duration in seconds')

    args = parser.parse_args()

    test = LoadTest(args.host, args.users, args.duration)
    asyncio.run(test.run_load_test())


if __name__ == '__main__':
    main()
