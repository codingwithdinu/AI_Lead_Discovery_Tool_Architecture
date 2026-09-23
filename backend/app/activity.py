from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field

SIGNAL_TYPES={"HIRING","FUNDING","PRODUCT_LAUNCH","TECHNOLOGY_ADOPTION","AI_INITIATIVE","CLOUD_MIGRATION","DIGITAL_TRANSFORMATION","EXPANSION","PARTNERSHIP","PROCUREMENT_INTENT","VENDOR_SEARCH","PAIN_POINT","LEADERSHIP_CHANGE","COMPANY_GROWTH","JOB_CHANGE","OTHER"}
INTENTS={"HIGH","MEDIUM","LOW","NONE"}

class LinkedInActivity(BaseModel):
    activity_id:str
    author_name:str
    author_url:HttpUrl|None=None
    author_title:str|None=None
    company:str|None=None
    post_url:HttpUrl
    published_at:datetime|None
    text:str=Field(min_length=1)
    source:str
    source_provider:str
    signal_type:str="OTHER"
    intent:str="NONE"
    evidence:str|None=None
    metadata:dict[str,str|int|float|bool|None]={}
