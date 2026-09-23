import os
import re
import httpx
from datetime import datetime,timezone,timedelta
from email.utils import parsedate_to_datetime
from app.activity import LinkedInActivity
from app.providers.base import LinkedInActivityProvider

class SerpApiLinkedInProvider(LinkedInActivityProvider):
    name="serpapi"

    def __init__(self):
        self.api_key=os.getenv("SERPAPI_KEY")

    @staticmethod
    def _parse_result_date(value:str|None,now:datetime)->datetime|None:
        if not value:
            return None
        text=value.strip()
        try:
            parsed=datetime.fromisoformat(text.replace("Z","+00:00"))
            if parsed.tzinfo is None:
                parsed=parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            pass

        relative=re.match(r"^(\d+)\s+(minute|minutes|hour|hours|day|days|week|weeks|month|months)\s+ago$",text,re.I)
        if relative:
            amount=int(relative.group(1))
            unit=relative.group(2).lower()
            if unit.startswith("minute"): delta=timedelta(minutes=amount)
            elif unit.startswith("hour"): delta=timedelta(hours=amount)
            elif unit.startswith("day"): delta=timedelta(days=amount)
            elif unit.startswith("week"): delta=timedelta(weeks=amount)
            elif unit.startswith("month"): delta=timedelta(days=30*amount)
            else: delta=timedelta(days=30*amount)
            return now-delta

        try:
            parsed=parsedate_to_datetime(text)
            if parsed.tzinfo is None:
                parsed=parsed.replace(tzinfo=timezone.utc)
            return parsed
        except (TypeError,ValueError):
            pass

        for fmt in ("%b %d, %Y","%B %d, %Y","%b %d","%B %d"):
            try:
                parsed=datetime.strptime(text,fmt).replace(tzinfo=timezone.utc)
                if parsed.year==1900:
                    parsed=parsed.replace(year=now.year)
                return parsed
            except ValueError:
                continue
        return None

    async def search(
        self,
        query:str,
        start:datetime,
        end:datetime,
        limit:int=100,
        country:str|None=None,
        location:str|None=None,
    )->list[LinkedInActivity]:
        if not self.api_key:
            raise RuntimeError("SERPAPI_KEY is not configured")

        params={
            "engine":"google",
            "q":f"site:linkedin.com/posts/ {query}",
            "api_key":self.api_key,
            "num":min(limit,100),
        }
        if country:
            country=country.lower()
            params["gl"]=country
            params["cr"]=f"country{country.upper()}"
        if location:
            params["location"]=location

        async with httpx.AsyncClient(timeout=30) as client:
            response=await client.get("https://serpapi.com/search.json",params=params)
            response.raise_for_status()
            data=response.json()

        activities=[]
        for item in data.get("organic_results",[]):
            url=item.get("link")
            if not url or "linkedin.com" not in url:
                continue

            published_at=self._parse_result_date(item.get("date"),end)
            if not published_at or not (start<=published_at<=end):
                continue

            title=item.get("title") or ""
            author=item.get("author") or title or "Unknown"
            snippet=item.get("snippet") or title or ""

            activities.append(
                LinkedInActivity(
                    activity_id=url,
                    author_name=author,
                    post_url=url,
                    published_at=published_at,
                    text=snippet,
                    source="linkedin",
                    source_provider=self.name,
                    metadata={
                        "search_country":country or "",
                        "search_location":location or "",
                    },
                )
            )
        return activities
