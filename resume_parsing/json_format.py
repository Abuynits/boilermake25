from typing import List, Optional
from pydantic import BaseModel, Field

################################ CSResume ################################

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


################################ CSJobPosting ################################

class Company(BaseModel):
    name: str = Field(..., description="Company name")
    website: Optional[str] = Field(None, description="Company website URL")
    location: Optional[str] = Field(None, description="Company location or headquarters")

class JobDescription(BaseModel):
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Detailed job description")
    responsibilities: Optional[List[str]] = Field(None, description="List of key responsibilities for the role")
    requirements: Optional[List[str]] = Field(None, description="List of required qualifications and skills")
    skills: Optional[List[str]] = Field(None, description="List of technical skills or proficiencies required")
    employmentType: Optional[str] = Field(None, description="Employment type (e.g., Full-Time, Part-Time, Contract)")
    experienceLevel: Optional[str] = Field(None, description="Experience level required (e.g., Entry-Level, Mid-Level, Senior)")
    salaryRange: Optional[str] = Field(None, description="Salary range offered (e.g., '$70k-$90k')")
    benefits: Optional[List[str]] = Field(None, description="List of benefits provided (e.g., Health Insurance, 401k)")
    postingDate: Optional[str] = Field(None, description="Job posting date in YYYY-MM-DD format")
    closingDate: Optional[str] = Field(None, description="Application closing date in YYYY-MM-DD format")

class ApplicationDetails(BaseModel):
    howToApply: Optional[str] = Field(None, description="Instructions for applying to the job")
    applicationURL: Optional[str] = Field(None, description="URL where candidates can submit their applications")
    contactEmail: Optional[str] = Field(None, description="Contact email for job-related inquiries")

class CSJobPosting(BaseModel):
    company: Company = Field(..., description="Company information")
    job: JobDescription = Field(..., description="Job details")
    application: Optional[ApplicationDetails] = Field(None, description="Application instructions and contact details")
