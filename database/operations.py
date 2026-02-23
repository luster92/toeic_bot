"""Database operations for TOEIC Bot."""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from .models import User, Question, Response, Progress


class DatabaseOperations:
    """CRUD operations for TOEIC Bot database."""
    
    def __init__(self, session: Session):
        self.session = session
    
    # User operations
    def get_or_create_user(self, telegram_id: int, username: str = None, first_name: str = None) -> User:
        """Get existing user or create new one."""
        user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
        
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name
            )
            self.session.add(user)
            self.session.commit()
        else:
            # Update last active
            user.last_active = datetime.utcnow()
            self.session.commit()
        
        return user
    
    def update_user_preferences(self, telegram_id: int, **kwargs) -> User:
        """Update user preferences."""
        user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.session.commit()
        return user
    
    def get_all_active_users(self) -> List[User]:
        """Get all active users for daily delivery."""
        return self.session.query(User).filter_by(is_active=True).all()
    
    # Question operations
    def save_question(self, question_data: Dict[str, Any]) -> Question:
        """Save a generated question."""
        question = Question(**question_data)
        self.session.add(question)
        self.session.commit()
        return question
    
    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        """Get question by ID."""
        return self.session.query(Question).filter_by(id=question_id).first()
    
    # Response operations
    def save_response(self, user_id: int, question_id: int, user_answer: str, 
                     time_taken: Optional[int] = None) -> Response:
        """Save user response and update progress."""
        question = self.get_question_by_id(question_id)
        is_correct = (user_answer.upper() == question.correct_answer.upper())
        
        response = Response(
            user_id=user_id,
            question_id=question_id,
            user_answer=user_answer.upper(),
            is_correct=is_correct,
            time_taken_seconds=time_taken
        )
        self.session.add(response)
        
        # Update question usage
        question.used_count += 1
        
        self.session.commit()
        
        # Update daily progress
        self._update_daily_progress(user_id)
        
        return response
    
    def _update_daily_progress(self, user_id: int):
        """Update daily progress for a user."""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get or create today's progress record
        progress = self.session.query(Progress).filter(
            and_(Progress.user_id == user_id, Progress.date == today)
        ).first()
        
        if not progress:
            progress = Progress(user_id=user_id, date=today)
            self.session.add(progress)
        
        # Calculate today's stats
        today_responses = self.session.query(Response).join(User).filter(
            and_(
                User.id == user_id,
                Response.answered_at >= today
            )
        ).all()
        
        if today_responses:
            progress.questions_attempted = len(today_responses)
            progress.questions_correct = sum(1 for r in today_responses if r.is_correct)
            progress.accuracy_percentage = (progress.questions_correct / progress.questions_attempted) * 100
            
            # Calculate by type
            for q_type in ['listening', 'grammar', 'vocabulary', 'reading']:
                type_responses = [r for r in today_responses if r.question.question_type == q_type]
                if type_responses:
                    type_correct = sum(1 for r in type_responses if r.is_correct)
                    type_accuracy = (type_correct / len(type_responses)) * 100
                    setattr(progress, f"{q_type}_accuracy", type_accuracy)
            
            # Estimate TOEIC score (simplified formula)
            progress.estimated_toeic_score = self._estimate_toeic_score(progress.accuracy_percentage)
            
            # Update user's current estimated score
            user = self.session.query(User).filter_by(id=user_id).first()
            user.current_estimated_score = progress.estimated_toeic_score
        
        self.session.commit()
    
    def _estimate_toeic_score(self, accuracy: float) -> int:
        """Estimate TOEIC score based on accuracy.
        
        Simplified mapping:
        - 90%+ accuracy → 800-900
        - 80-90% → 700-800
        - 70-80% → 600-700
        - 60-70% → 500-600
        - <60% → 400-500
        """
        if accuracy >= 90:
            return int(800 + (accuracy - 90) * 10)
        elif accuracy >= 80:
            return int(700 + (accuracy - 80) * 10)
        elif accuracy >= 70:
            return int(600 + (accuracy - 70) * 10)
        elif accuracy >= 60:
            return int(500 + (accuracy - 60) * 10)
        else:
            return int(400 + accuracy * 1.67)
    
    # Progress operations
    def get_user_progress(self, telegram_id: int, days: int = 7) -> List[Progress]:
        """Get user progress for the last N days."""
        user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return []
        
        start_date = datetime.utcnow() - timedelta(days=days)
        return self.session.query(Progress).filter(
            and_(
                Progress.user_id == user.id,
                Progress.date >= start_date
            )
        ).order_by(Progress.date.desc()).all()
    
    def get_weak_areas(self, telegram_id: int, days: int = 7) -> Dict[str, float]:
        """Identify weak areas based on recent performance."""
        progress_records = self.get_user_progress(telegram_id, days)
        
        if not progress_records:
            return {}
        
        # Calculate average accuracy by type
        weak_areas = {}
        for q_type in ['listening', 'grammar', 'vocabulary', 'reading']:
            accuracies = [
                getattr(p, f"{q_type}_accuracy") 
                for p in progress_records 
                if getattr(p, f"{q_type}_accuracy") is not None
            ]
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                weak_areas[q_type] = avg_accuracy
        
        # Sort by accuracy (lowest first = weakest)
        return dict(sorted(weak_areas.items(), key=lambda x: x[1]))
    
    def get_user_stats(self, telegram_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return {}
        
        # Get all responses
        total_responses = self.session.query(Response).filter_by(user_id=user.id).count()
        correct_responses = self.session.query(Response).filter_by(
            user_id=user.id, is_correct=True
        ).count()
        
        overall_accuracy = (correct_responses / total_responses * 100) if total_responses > 0 else 0
        
        # Get recent progress
        recent_progress = self.get_user_progress(telegram_id, days=7)
        weak_areas = self.get_weak_areas(telegram_id, days=7)
        
        # Calculate streak
        streak = self._calculate_streak(user.id)
        
        return {
            'total_questions': total_responses,
            'overall_accuracy': overall_accuracy,
            'current_score': user.current_estimated_score,
            'target_score': user.target_score,
            'progress_to_goal': (user.current_estimated_score / user.target_score) * 100,
            'weak_areas': weak_areas,
            'recent_progress': recent_progress,
            'streak_days': streak
        }
    
    def _calculate_streak(self, user_id: int) -> int:
        """Calculate consecutive days of activity."""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        streak = 0
        
        for i in range(365):  # Check up to 1 year
            check_date = today - timedelta(days=i)
            has_activity = self.session.query(Progress).filter(
                and_(
                    Progress.user_id == user_id,
                    Progress.date == check_date,
                    Progress.questions_attempted > 0
                )
            ).first()
            
            if has_activity:
                streak += 1
            else:
                break
        
        return streak
