from django.db.models import Q, F
from django.utils import timezone
from .models import User, MatchProfile, Match, ChatRoom
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class MatchingEngine:
    def __init__(self):
        self.weights = {
            'interests': 0.35,
            'location': 0.25,
            'age': 0.20,
            'height': 0.15,
            'education': 0.05,
        }
    
    def find_candidates(self, user, limit=50):
        profile = user.match_profile
        if not profile or not profile.is_active:
            return []
        
        candidates = self._get_candidates_by_scope(user, profile)
        candidates = self._apply_filters(candidates, user, profile)
        candidates = self._apply_mode_filter(candidates, user, profile)
        
        candidates = candidates[:limit]
        return candidates
    
    def _get_candidates_by_scope(self, user, profile):
        base_query = User.objects.filter(
            is_verified=True,
            is_banned=False,
            is_institutional=True,
        ).exclude(id=user.id)
        
        if profile.scope == 'same_institute':
            user_domain = user.email.split('@')[1]
            return base_query.filter(email__iendswith=f'@{user_domain}')
        
        elif profile.scope == 'city':
            return base_query.filter(city=user.city)
        
        elif profile.scope == 'state':
            return base_query.filter(state=user.state)
        
        elif profile.scope == 'national':
            return base_query.filter(country=user.country)
        
        else:
            return base_query
    
    def _apply_filters(self, candidates, user, profile):
        candidates = candidates.filter(
            age__gte=profile.age_range_min,
            age__lte=profile.age_range_max,
        )
        
        if profile.height_range_min_cm and user.height_cm:
            candidates = candidates.filter(
                height_cm__gte=profile.height_range_min_cm,
                height_cm__lte=profile.height_range_max_cm,
            )
        
        existing_matches = Match.objects.filter(
            Q(user_a=user, expires_at__gt=timezone.now()) |
            Q(user_b=user, expires_at__gt=timezone.now())
        ).values_list('user_a_id', 'user_b_id')
        
        exclude_ids = set()
        for a_id, b_id in existing_matches:
            exclude_ids.add(a_id)
            exclude_ids.add(b_id)
        
        candidates = candidates.exclude(id__in=exclude_ids)
        
        return candidates.order_by('?')[:100]
    
    def _apply_mode_filter(self, candidates, user, profile):
        if profile.preferred_mode == 'hookup':
            user_gender = user.gender
            if user_gender == 'M':
                return candidates.filter(gender='F')
            elif user_gender == 'F':
                return candidates.filter(gender='M')
            else:
                return candidates
        
        return candidates
    
    def validate_mode(self, user_a, user_b, mode):
        if mode == 'friend':
            return True
        
        elif mode == 'hookup':
            if not user_a.gender or not user_b.gender:
                return False
            
            if user_a.gender == user_b.gender:
                return False
            
            if user_a.gender not in ['M', 'F'] or user_b.gender not in ['M', 'F']:
                return False
            
            return True
        
        return False
    
    def calculate_score(self, user_a, user_b):
        scores = {}
        
        scores['interests'] = self._score_interests(user_a, user_b)
        scores['location'] = self._score_location(user_a, user_b)
        scores['age'] = self._score_age(user_a, user_b)
        scores['height'] = self._score_height(user_a, user_b)
        scores['education'] = self._score_education(user_a, user_b)
        
        total_score = sum(
            scores[key] * self.weights[key]
            for key in scores
        )
        
        return min(100, max(0, total_score))
    
    def _score_interests(self, user_a, user_b):
        interests_a = set(user_a.interests) if user_a.interests else set()
        interests_b = set(user_b.interests) if user_b.interests else set()
        
        if not interests_a or not interests_b:
            return 50
        
        intersection = len(interests_a & interests_b)
        union = len(interests_a | interests_b)
        
        if union == 0:
            return 0
        
        return (intersection / union) * 100
    
    def _score_location(self, user_a, user_b):
        if user_a.city and user_b.city and user_a.city == user_b.city:
            return 100
        elif user_a.state and user_b.state and user_a.state == user_b.state:
            return 75
        elif user_a.country and user_b.country and user_a.country == user_b.country:
            return 50
        else:
            return 25
    
    def _score_age(self, user_a, user_b):
        if not user_a.age or not user_b.age:
            return 50
        
        age_diff = abs(user_a.age - user_b.age)
        if age_diff <= 2:
            return 100
        elif age_diff <= 5:
            return 80
        elif age_diff <= 10:
            return 60
        elif age_diff <= 15:
            return 40
        else:
            return 20
    
    def _score_height(self, user_a, user_b):
        if not user_a.height_cm or not user_b.height_cm:
            return 50
        
        height_diff = abs(user_a.height_cm - user_b.height_cm)
        if height_diff <= 5:
            return 100
        elif height_diff <= 10:
            return 80
        elif height_diff <= 20:
            return 60
        elif height_diff <= 30:
            return 40
        else:
            return 20
    
    def _score_education(self, user_a, user_b):
        if user_a.degree and user_b.degree and user_a.degree.lower() == user_b.degree.lower():
            return 100
        elif user_a.profession and user_b.profession and user_a.profession.lower() == user_b.profession.lower():
            return 80
        else:
            return 50
