from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl

class LeadCreate(BaseModel):
    full_name:str
    job_title:str|None=None
    company:str|None=None
    location:str|None=None
    linkedin_url:HttpUrl|None=None
    post_url:HttpUrl|None=None
    post_date:datetime|None=None
    signal_type:str="OTHER"
    intent:str="NONE"
    evidence:str|None=None
    source:str="unknown"
    score:float=0

class LeadOut(LeadCreate):
    id:int
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)
