from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.counseling_note import CounselingNote
from app.models.student import Student
from app.models.user import User
from app.schemas.counseling import CounselingNoteCreate, CounselingNoteResponse
from app.services.auth import get_current_user
from app.services.kakao import kakao_service

router = APIRouter(prefix="/counseling", tags=["상담"])


@router.post("/notes", response_model=CounselingNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_counseling_note(
    note_data: CounselingNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """상담 노트 작성"""
    # 학생 조회
    student = db.query(Student).filter(Student.id == note_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
    
    # 상담 노트 생성
    note = CounselingNote(**note_data.dict())
    db.add(note)
    db.commit()
    db.refresh(note)
    
    # 학부모에게 카카오톡 알림 발송 (visibility가 SHARED인 경우만)
    if note.visibility == "SHARED":
        try:
            await kakao_service.send_counseling_notification(
                db=db,
                parent_phone=student.parent_phone,
                student_name=student.name,
                counseling_content=note.content
            )
        except Exception as e:
            print(f"상담 알림 발송 실패: {e}")
    
    return note


@router.get("/notes/student/{student_id}", response_model=List[CounselingNoteResponse])
async def get_student_counseling_notes(
    student_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """학생별 상담 노트 조회"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
    
    notes = db.query(CounselingNote)\
        .filter(CounselingNote.student_id == student_id)\
        .order_by(CounselingNote.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return notes

