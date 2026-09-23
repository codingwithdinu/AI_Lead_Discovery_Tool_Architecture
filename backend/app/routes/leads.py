from datetime import date,timedelta
from fastapi import APIRouter,Depends,Query
from sqlalchemy import select,or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Lead
from app.schemas import LeadCreate,LeadOut

router=APIRouter(prefix="/leads",tags=["leads"])

@router.get("",response_model=list[LeadOut])
async def list_leads(q:str|None=None,min_score:float=0,signal_type:str|None=None,intent:str|None=None,db:AsyncSession=Depends(get_db)):
    stmt=select(Lead).where(Lead.score>=min_score).order_by(Lead.score.desc())
    if q: stmt=stmt.where(or_(Lead.full_name.ilike(f"%{q}%"),Lead.company.ilike(f"%{q}%"),Lead.job_title.ilike(f"%{q}%")))
    if signal_type: stmt=stmt.where(Lead.signal_type==signal_type)
    if intent: stmt=stmt.where(Lead.intent==intent)
    return list((await db.scalars(stmt)).all())

@router.post("",response_model=LeadOut,status_code=201)
async def create_lead(data:LeadCreate,db:AsyncSession=Depends(get_db)):
    values=data.model_dump()
    if values.get("linkedin_url"): values["linkedin_url"]=str(values["linkedin_url"])
    if values.get("post_url"): values["post_url"]=str(values["post_url"])
    lead=Lead(**values); db.add(lead); await db.commit(); await db.refresh(lead); return lead

@router.get("/date-range")
async def date_range(kind:str=Query("previous_month")):
    today=date.today()
    if kind=="current_month":
        start=today.replace(day=1); end=(start.replace(day=28)+timedelta(days=4)).replace(day=1)-timedelta(days=1)
    else:
        end=today.replace(day=1)-timedelta(days=1); start=end.replace(day=1); kind="previous_month"
    return {"type":kind,"start":start.isoformat(),"end":end.isoformat()}
