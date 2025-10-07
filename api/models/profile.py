# api/models/profile.py
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import List, Optional

class Header(BaseModel):
    name: str = Field("", max_length=120)
    title: str = Field("", max_length=160)

class Contact(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=40)
    website: Optional[HttpUrl] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = Field(None, max_length=120)

class Project(BaseModel):
    title: str = Field(..., max_length=140)
    desc: str = Field("", max_length=600)
    url: Optional[str] = None

class Education(BaseModel):
    title: str = ""
    school: str = ""
    start: str = ""
    end: str = ""
    details: str = ""
    url: Optional[str] = None

class Profile(BaseModel):
    header: Header = Header()
    contact: Contact = Contact()
    summary: List[str] = []
    skills: List[str] = []
    languages: List[str] = []
    projects: List[Project] = []
    education: List[Education] = []
    avatar: Optional[str] = None  # مسار صورة داخلي إن رغبت
