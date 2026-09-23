from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Lead(Base):
    __tablename__="leads"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    full_name: Mapped[str]=mapped_column(String(200),index=True)
    job_title: Mapped[str|None]=mapped_column(String(200))
    company: Mapped[str|None]=mapped_column(String(200),index=True)
    location: Mapped[str|None]=mapped_column(String(200))
    linkedin_url: Mapped[str|None]=mapped_column(String(500),unique=True)
    post_url: Mapped[str|None]=mapped_column(String(1000))
    post_date: Mapped[datetime|None]=mapped_column(DateTime)
    signal_type: Mapped[str]=mapped_column(String(60),default="OTHER",index=True)
    intent: Mapped[str]=mapped_column(String(20),default="NONE",index=True)
    evidence: Mapped[str|None]=mapped_column(Text)
    source: Mapped[str]=mapped_column(String(100),default="unknown")
    score: Mapped[float]=mapped_column(Float,default=0,index=True)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
