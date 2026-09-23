from datetime import datetime,timezone,timedelta
from fastapi import APIRouter,HTTPException,Query,Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Lead
from app.providers.factory import get_linkedin_provider
from app.intent import detect_signal

router=APIRouter(prefix="/activity",tags=["linkedin-activity"])

@router.get("/linkedin/search")
async def search_linkedin_activity(
    q:str=Query(...,min_length=2),
    days:int=Query(30,ge=1,le=365),
    limit:int=Query(25,ge=1,le=100),
    country:str|None=Query(None,min_length=2,max_length=2),
    location:str|None=Query(None,max_length=200),
    db:AsyncSession=Depends(get_db),
):
    end=datetime.now(timezone.utc)
    start=end-timedelta(days=days)
    try:
        provider=get_linkedin_provider()
        activities=await provider.search(q,start,end,limit,country=country,location=location)
    except RuntimeError as exc:
        message=str(exc)
        if "SERPAPI_KEY" in message:
            message="LinkedIn activity search is not configured yet. Add SERPAPI_KEY to the Render backend environment, then redeploy."
        raise HTTPException(status_code=503,detail=message)

    stored=0
    for activity in activities:
        signal,intent,score,evidence=detect_signal(activity.text)
        activity.signal_type=signal
        activity.intent=intent
        activity.evidence=evidence

        existing=await db.scalar(select(Lead).where(Lead.post_url==str(activity.post_url)))
        if existing:
            continue

        lead=Lead(
            full_name=activity.author_name,
            job_title=activity.author_title,
            company=activity.company,
            linkedin_url=str(activity.author_url) if activity.author_url else None,
            post_url=str(activity.post_url),
            post_date=activity.published_at,
            signal_type=signal,
            intent=intent,
            evidence=activity.text,
            source=f"{activity.source}/{activity.source_provider}",
            score=score,
        )
        db.add(lead)
        stored += 1

    if stored:
        await db.commit()

    return {
        "provider":provider.name,
        "count":len(activities),
        "stored":stored,
        "filters":{"country":country,"location":location},
        "items":[a.model_dump(mode="json") for a in activities],
    }
