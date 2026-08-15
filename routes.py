from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import datetime
from app.models.schemas import (
    StudentProfile, MentorChatRequest, RoadmapRequest, 
    SkillGapRequest, ResumeAnalyzeRequest
)
from app.services.db_service import DatabaseService
from ai.services.gemini_service import GeminiService

router = APIRouter()

# Dependency providers
def get_db_service():
    return DatabaseService()

def get_gemini_service():
    return GeminiService()

@router.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.utcnow().isoformat()}

# 1. Student Profile Router
@router.get("/student/{student_id}", response_model=StudentProfile)
def get_student(student_id: str, db: DatabaseService = Depends(get_db_service)):
    profile = db.get_student_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return profile

@router.post("/student/{student_id}")
def update_student(student_id: str, profile: StudentProfile, db: DatabaseService = Depends(get_db_service)):
    success = db.save_student_profile(student_id, profile.model_dump())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save student profile")
    return {"status": "success", "message": "Profile updated"}

# 2. AI Learning Mentor Chat
@router.post("/mentor/chat")
def chat_with_mentor(request: MentorChatRequest, ai: GeminiService = Depends(get_gemini_service)):
    reply = ai.generate_chat_response(request.message)
    return {"reply": reply, "timestamp": datetime.datetime.utcnow().isoformat()}

# 3. Personalized Roadmap Generator
@router.post("/roadmap/generate")
def generate_roadmap(
    request: RoadmapRequest, 
    db: DatabaseService = Depends(get_db_service), 
    ai: GeminiService = Depends(get_gemini_service)
):
    student = db.get_student_profile(request.student_id)
    career = db.get_career_profile(request.target_career_id)
    
    if not student or not career:
        raise HTTPException(status_code=404, detail="Student profile or Career target not found")

    roadmap = ai.generate_personalized_roadmap(student, career)
    
    # Enrich with metadata
    roadmap["student_id"] = request.student_id
    roadmap["career_id"] = request.target_career_id
    roadmap["created_at"] = datetime.datetime.utcnow().isoformat()
    
    # Save to database
    db.save_generated_roadmap(request.student_id, roadmap)
    return roadmap

# 4. Skill Gap Analyzer
@router.post("/skillgap/analyze")
def analyze_skill_gap(
    request: SkillGapRequest, 
    db: DatabaseService = Depends(get_db_service), 
    ai: GeminiService = Depends(get_gemini_service)
):
    student = db.get_student_profile(request.student_id)
    career = db.get_career_profile(request.target_career_id)
    
    if not student or not career:
        raise HTTPException(status_code=404, detail="Student or Career profile not found")
        
    student_skills = student.get("skills", {})
    career_skills = career.get("required_skills", {})
    
    analysis = ai.analyze_skill_gap(student_skills, career_skills)
    analysis["created_at"] = datetime.datetime.utcnow().isoformat()
    
    return analysis

# 5. Resume Feedback Analyzer
@router.post("/resume/analyze")
def analyze_resume(
    request: ResumeAnalyzeRequest, 
    db: DatabaseService = Depends(get_db_service), 
    ai: GeminiService = Depends(get_gemini_service)
):
    career = db.get_career_profile(request.target_career_id)
    if not career:
        raise HTTPException(status_code=404, detail="Target career profile not found")
        
    resume_text = request.resume_text or "Experienced in Python programming and databases, looking for ML Engineer roles."
    analysis = ai.analyze_resume_alignment(resume_text, career)
    analysis["created_at"] = datetime.datetime.utcnow().isoformat()
    
    return analysis
