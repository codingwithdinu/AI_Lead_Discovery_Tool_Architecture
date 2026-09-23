from fastapi import APIRouter, Query
from datetime import date
router=APIRouter(prefix="/leads", tags=["leads"])

DEMO_LEADS=[
 {"id":1,"full_name":"Example CTO","job_title":"CTO","company":"Example AI","location":"India","score":91,"signal_type":"AI_INITIATIVE","intent":"HIGH","post_date":"2026-08-15","post_url":"https://www.linkedin.com/","source":"linkedin_via_search"},
 {"id":2,"full_name":"Example Founder","job_title":"Founder","company":"Cloud Startup","location":"India","score":84,"signal_type":"HIRING","intent":"MEDIUM","post_date":"2026-08-10","post_url":"https://www.linkedin.com/","source":"linkedin_via_search"},
]

@router.get("")
async def list_leads(q:str|None=None,min_score:int=0,status:str|None=None,signal_type:str|None=None):
    rows=[x for x in DEMO_LEADS if x["score"]>=min_score]
    if q: rows=[x for x in rows if q.lower() in (x["full_name"]+" "+x["company"]+" "+x["job_title"]).lower()]
    if signal_type: rows=[x for x in rows if x["signal_type"]==signal_type]
    return {"items":rows,"total":len(rows)}

@router.get("/date-range")
async def date_range(kind:str=Query("previous_month")):
    today=date.today()
    if kind=="current_month":
        start=today.replace(day=1)
        if today.month==12: end=date(today.year,12,31)
        else:
            from datetime import timedelta
            end=today.replace(day=28)+timedelta(days=4)
            end=end.replace(day=1)-timedelta(days=1)
    else:
        year=today.year if today.month>1 else today.year-1
        month=today.month-1 if today.month>1 else 12
        start=date(year,month,1)
        if month==12: end=date(year,12,31)
        else:
            from datetime import timedelta
            end=date(year,month,28)+timedelta(days=4)
            end=end.replace(day=1)-timedelta(days=1)
    return {"type":kind,"start":start.isoformat(),"end":end.isoformat()}
