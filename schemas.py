from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

# Auth schemas
class UserLogin(BaseModel):
    email: str
    password: str

# Student Profiles
class AcademicDetails(BaseModel):
    major: str
    gpa: float
    year_of_study: int
    completed_courses: List[str] = []

class StudentSkills(BaseModel):
    skills: Dict[str, int] = {} # e.g. {"Python": 4, "SQL": 3}

class StudentProfile(BaseModel):
    student_id: str
    name: str
    email: str
    academic_details: AcademicDetails
    skills: Dict[str, int] = {}
    interests: List[str] = []
    career_goals: List[str] = []
    resume_url: Optional[str] = None

# AI Service input schemas
class MentorChatRequest(BaseModel):
    message: str
    student_id: str

class RoadmapRequest(BaseModel):
    student_id: str
    target_career_id: str

class SkillGapRequest(BaseModel):
    student_id: str
    target_career_id: str

class ResumeAnalyzeRequest(BaseModel):
    student_id: str
    target_career_id: str
    resume_text: Optional[str] = None
