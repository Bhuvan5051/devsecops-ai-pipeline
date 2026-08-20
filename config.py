"""
config.py

Application configuration.

--- Intentional vulnerability (Project 5 deliberate fail commit): ---
Hardcoded API key committed directly to source control instead of being
loaded from an environment variable or secrets manager. This is exactly
what Gate 3 (Gitleaks) is designed to catch.
"""

API_KEY = "sk-live-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
