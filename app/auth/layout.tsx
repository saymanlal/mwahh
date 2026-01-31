import React from "react"
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Authentication - Matchmaking Platform',
  description: 'Sign up or verify your campus email',
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Matchmaking</h1>
            <p className="text-gray-600 mt-2">Campus-verified connections</p>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
