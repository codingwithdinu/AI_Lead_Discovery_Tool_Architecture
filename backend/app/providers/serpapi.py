import os
import re
import httpx
from datetime import datetime,timezone,timedelta
from email.utils import parsedate_to_datetime
from app.activity import LinkedInActivity
from app.providers.base import LinkedInActivityProvider

CATEGORY_TERMS = {
    "all": "",
    "job_posts": '(site:linkedin.com/jobs/view OR site:linkedin.com/posts OR site:linkedin.com/feed/update)',
    "software_requirements": '(site:linkedin.com/posts OR site:linkedin.com/feed/update) ("looking for software" OR "need software" OR "software development" OR "IT services" OR "software requirement" OR "website development" OR "app development")',
    "ai_cloud": '(site:linkedin.com/posts OR site:linkedin.com/feed/update) ("AI solution" OR "AI automation" OR "machine learning" OR "cloud migration" OR "cloud services" OR "AI development")',
    "vendor_search": '(site:linkedin.com/posts OR site:linkedin.com/feed/update) ("looking for a vendor" OR "looking for an agency" OR "seeking software company" OR "looking for a development partner" OR "IT vendor")',
}

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
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
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
            else: delta=timedelta(days=30*amount)
            return now-delta
        try:
            parsed=parsedate_to_datetime(text)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except (TypeError,ValueError):
            pass
        for fmt in ("%b %d, %Y","%B %d, %Y","%b %d","%B %d"):
            try:
                parsed=datetime.strptime(text,fmt).replace(tzinfo=timezone.utc)
                return parsed.replace(year=now.year) if parsed.year==1900 else parsed
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
        category:str="all",
    )->list[LinkedInActivity]:
        if not self.api_key:
            raise RuntimeError("SERPAPI_KEY is not configured")
        if category not in CATEGORY_TERMS:
            raise ValueError("Unsupported search category")

        # Category query terms are combined with user keywords; no result is synthesized.
        category_query=CATEGORY_TERMS[category]
        if category=="all":
            sites="(site:linkedin.com/posts OR site:linkedin.com/feed/update OR site:linkedin.com/jobs/view)"
            search_query=f'{sites} {query}'
        else:
            search_query=f'{category_query} {query}'
        if location:
            search_query += f' "{location}"'

        params={
            "engine":"google",
            "q":search_query,
            "api_key":self.api_key,
            "num":min(limit,100),
            "tbs":f"cdr:1,cd_min:{start.month}/{start.day}/{start.year},cd_max:{end.month}/{end.day}/{end.year}",
        }
        if country:
            params["gl"]=country.lower()
            params["cr"]=f"country{country.upper()}"
        if location:
            params["location"]=location

        async with httpx.AsyncClient(timeout=35) as client:
            response=await client.get("https://serpapi.com/search.json",params=params)
            response.raise_for_status()
            data=response.json()

        activities=[]
        for item in data.get("organic_results",[]):
            url=item.get("link")
            if not url or "linkedin.com" not in url:
                continue
            published_at=self._parse_result_date(item.get("date"),end)
            # Google's date-range operator is applied to the query. If a result
            # exposes a parseable date, enforce the requested window locally too.
            if published_at and not (start<=published_at<=end):
                continue
            title=item.get("title") or ""
            author=item.get("author") or item.get("source") or "Author not identified"
            snippet=item.get("snippet") or title
            if not snippet.strip():
                continue
            activities.append(LinkedInActivity(
                activity_id=url,
                author_name=author,
                post_url=url,
                published_at=published_at,
                text=snippet,
                source="linkedin_public_search",
                source_provider=self.name,
                metadata={
                    "search_country":country or "",
                    "search_location":location or "",
                    "search_category":category,
                    "result_title":title,
                    "result_type":"job_post" if "linkedin.com/jobs/view" in url else "linkedin_post",
                },
            ))
        return activities
