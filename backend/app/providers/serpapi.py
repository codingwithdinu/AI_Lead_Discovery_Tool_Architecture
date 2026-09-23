import os
import httpx
from datetime import datetime
from app.activity import LinkedInActivity
from app.providers.base import LinkedInActivityProvider

class SerpApiLinkedInProvider(LinkedInActivityProvider):
    name="serpapi"

    def __init__(self):
        self.api_key=os.getenv("SERPAPI_KEY")

    async def search(self,query:str,start:datetime,end:datetime,limit:int=100)->list[LinkedInActivity]:
        if not self.api_key:
            raise RuntimeError("SERPAPI_KEY is not configured")
        params={"engine":"google","q":f"site:linkedin.com/posts/ {query}","api_key":self.api_key,"num":min(limit,100)}
        async with httpx.AsyncClient(timeout=30) as client:
            response=await client.get("https://serpapi.com/search.json",params=params)
            response.raise_for_status()
            data=response.json()
        activities=[]
        for item in data.get("organic_results",[]):
            url=item.get("link")
            title=item.get("title")
            snippet=item.get("snippet")
            if not url or "linkedin.com" not in url: continue
            # Search providers do not reliably expose publication timestamps.
            # Never invent one: only accept an explicit parseable date.
            published=item.get("date")
            if not published: continue
            try: published_at=datetime.fromisoformat(published.replace("Z","+00:00"))
            except ValueError: continue
            if not (start<=published_at<=end): continue
            activities.append(LinkedInActivity(activity_id=url,author_name=title or "Unknown",post_url=url,published_at=published_at,text=snippet or title or "",source="linkedin",source_provider=self.name))
        return activities
