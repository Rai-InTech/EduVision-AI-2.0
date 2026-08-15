import os
import json
import logging
from typing import Dict, Any, List, Optional
import firebase_admin
from firebase_admin import credentials, firestore #type:ignore
from config.config import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.db = None
        self.mock_mode = True
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initializes Firebase Firestore using service credentials."""
        cred_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        
        # Check if the service account file actually exists
        if os.path.exists(cred_path):
            try:
                # Check if app is already initialized
                if not firebase_admin._apps:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {
                        'projectId': settings.FIREBASE_PROJECT_ID,
                        'storageBucket': settings.CLOUD_STORAGE_BUCKET
                    })
                self.db = firestore.client()
                self.mock_mode = False
                logger.info("Firebase Firestore client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase SDK: {str(e)}. Running in mock database mode.")
        else:
            logger.warning(f"Firebase credentials not found at '{cred_path}'. Running in local database mock mode.")

    # Students CRUD
    def get_student_profile(self, student_id: str) -> Optional[Dict[str, Any]]:
        if self.mock_mode:
            # Read from static sample data file
            static_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "data", "sample_data", "student", "student_profiles.json"
            ))
            try:
                if os.path.exists(static_path):
                    with open(static_path, "r", encoding="utf-8") as f:
                        profiles = json.load(f)
                        for p in profiles:
                            if p["student_id"] == student_id:
                                return p
            except Exception as e:
                logger.error(f"Error reading mock student data: {str(e)}")
            
            # Default fallback mock object
            return {
                "student_id": student_id,
                "name": "Mock Student",
                "email": "student@edu.vision",
                "academic_details": {"major": "Computer Science", "gpa": 3.5, "year_of_study": 3, "completed_courses": []},
                "skills": {"Python": 3, "SQL": 2},
                "interests": ["Cloud"],
                "career_goals": ["Cloud Solutions Architect"]
            }
        
        # Live Firestore flow
        try:
            doc_ref = self.db.collection("students").document(student_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Firestore get student error: {str(e)}")
            return None

    def save_student_profile(self, student_id: str, profile_data: Dict[str, Any]) -> bool:
        if self.mock_mode:
            logger.info(f"[Mock Mode] Save student profile for {student_id}")
            return True
        try:
            self.db.collection("students").document(student_id).set(profile_data, merge=True)
            return True
        except Exception as e:
            logger.error(f"Firestore save student error: {str(e)}")
            return False

    # Career Catalog
    def get_career_profile(self, career_id: str) -> Optional[Dict[str, Any]]:
        if self.mock_mode:
            # Read from static career catalog
            static_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "data", "sample_data", "career", "career_catalog.json"
            ))
            try:
                if os.path.exists(static_path):
                    with open(static_path, "r", encoding="utf-8") as f:
                        catalog = json.load(f)
                        for c in catalog:
                            if c["career_id"] == career_id:
                                return c
            except Exception as e:
                logger.error(f"Error reading mock career data: {str(e)}")
            return {
                "career_id": career_id,
                "title": "Cloud Solutions Architect",
                "description": "Architects modern infrastructure.",
                "required_skills": {"Cloud Architectures (GCP/AWS)": 4, "Python": 3}
            }
            
        try:
            doc_ref = self.db.collection("careers").document(career_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Firestore get career error: {str(e)}")
            return None

    # Roadmap collection helpers
    def save_generated_roadmap(self, student_id: str, roadmap: Dict[str, Any]) -> bool:
        if self.mock_mode:
            logger.info(f"[Mock Mode] Save roadmap for {student_id}")
            return True
        try:
            # Add to subcollection of student
            doc_ref = self.db.collection("students").document(student_id).collection("roadmaps").document()
            doc_ref.set(roadmap)
            return True
        except Exception as e:
            logger.error(f"Firestore save roadmap error: {str(e)}")
            return False
            
    def get_latest_roadmap(self, student_id: str) -> Optional[Dict[str, Any]]:
        if self.mock_mode:
            return None
        try:
            docs = self.db.collection("students").document(student_id).collection("roadmaps")\
                .order_by("created_at", direction=firestore.Query.DESCENDING).limit(1).stream()
            for doc in docs:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Firestore get roadmaps error: {str(e)}")
            return None
