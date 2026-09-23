from datetime import datetime,timezone,timedelta
from fastapi import APIRouter,HTTPException,Query
from app.providers.factory import get_linkedin_provider

router=APIRouter(prefix="/activity",tags=["linkedin-activity"])

@router.get("/linkedin/search")
async def search_linkedin_activity(q:str=Query(...,min_length=2),days:int=Query(30,ge=1,le=365),limit:int=Query(25,ge=1,le=100)):
    end=datetime.now(timezone.utc)
    start=end-timedelta(days=days)
    try:
        provider=get_linkedin_provider()
        activities=await provider.search(q,start,end,limit)
    except RuntimeError as exc:
        message=str(exc)
        if "SERPAPI_KEY" in message:
            message="LinkedIn activity search is not configured yet. Add SERPAPI_KEY to the Render backend environment, then redeploy."
        raise HTTPException(status_code=503,detail=message)
    return {"provider":provider.name,"count":len(activities),"items":[a.model_dump(mode="json") for a in activities]}
