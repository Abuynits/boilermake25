from typing import List, Optional
from pydantic import BaseModel, Field

class Links(BaseModel):
    github: Optional[str] = Field(None, description="GitHub profile URL")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    website: Optional[str] = Field(None, description="Personal website URL")

class Personal(BaseModel):
    name: str = Field(..., description="Candidate's full name")
    email: str = Field(..., description="Candidate's email address")
    phone: Optional[str] = Field(None, description="Candidate's phone number")
    links: Optional[Links] = Field(None, description="Candidate's online profiles")

class Education(BaseModel):
    institution: str = Field(..., description="Name of the educational institution")
    degree: str = Field(..., description="Degree earned or pursued")
    startDate: str = Field(..., description="Start date in YYYY-MM-DD format")
    endDate: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    gpa: Optional[str] = Field(None, description="Grade Point Average")

class Experience(BaseModel):
    company: str = Field(..., description="Company name")
    role: str = Field(..., description="Role or job title")
    startDate: str = Field(..., description="Start date in YYYY-MM-DD format")
    endDate: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    highlights: Optional[List[str]] = Field(None, description="List of key responsibilities or achievements")

class Project(BaseModel):
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Brief description of the project")
    url: Optional[str] = Field(None, description="URL to the project")
    technologies: Optional[List[str]] = Field(None, description="List of technologies used")

class Certification(BaseModel):
    title: str = Field(..., description="Certification title")
    issuer: str = Field(..., description="Issuing organization")
    date: str = Field(..., description="Certification date in YYYY-MM-DD format")

class Award(BaseModel):
    title: str = Field(..., description="Award title")
    awarder: str = Field(..., description="Organization granting the award")
    date: str = Field(..., description="Award date in YYYY-MM-DD format")

class CSResume(BaseModel):
    personal: Personal = Field(..., description="Personal information")
    education: Optional[List[Education]] = Field(None, description="List of education entries")
    experience: List[Experience] = Field(..., description="List of work experiences")
    projects: List[Project] = Field(..., description="List of projects")
    skills: List[str] = Field(..., description="List of skills")
    certifications: Optional[List[Certification]] = Field(None, description="List of certifications")
    awards: Optional[List[Award]] = Field(None, description="List of awards")
