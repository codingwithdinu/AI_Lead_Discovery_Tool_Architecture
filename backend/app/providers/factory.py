import os
from app.providers.base import LinkedInActivityProvider
from app.providers.serpapi import SerpApiLinkedInProvider

def get_linkedin_provider()->LinkedInActivityProvider:
    provider=os.getenv("LINKEDIN_ACTIVITY_PROVIDER","serpapi").lower()
    if provider=="serpapi": return SerpApiLinkedInProvider()
    raise RuntimeError(f"Unsupported LinkedIn activity provider: {provider}")
