"""
Homework Management API V2
숙제 관리 시스템 (반 기반 + 파일 업로드)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date, timezone

from app.models.schemas import (
    HomeworkCreate, HomeworkUpdate, HomeworkResponse,
    HomeworkSubmissionCreate, HomeworkSubmissionResponse,
    PresignedUploadRequest, PresignedUploadResponse,
    TokenData
)
from app.auth.utils import require_admin
from app.database import supabase_admin

router = APIRouter(prefix="/homeworks", tags=["Homework"])


# ============================================
# Admin: Homework Management
# ============================================

@router.post("/", response_model=HomeworkResponse)
async def create_homework(
    homework: HomeworkCreate,
    current_user: TokenData = Depends(require_admin)
):
    """
    Create a new homework assignment
    
    시퀀스:
    1. homework 생성
    2. class_ids에 속한 학생들 조회
    3. homework_targets 스냅샷 저장
    4. (선택) 알림톡 발송
    """
    
    homework_data = homework.dict()
    homework_data["academy_id"] = str(current_user.academy_id)
    homework_data["created_by"] = str(current_user.user_id)
    
    # Convert date to string
    if homework_data.get("due_date"):
        homework_data["due_date"] = homework_data["due_date"].isoformat()
    
    # Convert class_ids to JSON
    homework_data["class_ids"] = [str(cid) for cid in homework_data.get("class_ids", [])]
    
    # 1. Create homework
    response = supabase_admin.table("homework")\
        .insert(homework_data)\
        .execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="숙제 생성에 실패했습니다"
        )
    
    homework_id = response.data[0]["id"]
    
    # 2. Get target students from classes
    target_students = []
    
    if homework.class_ids:
        for class_id in homework.class_ids:
            # Get students in this class
            members_response = supabase_admin.table("class_members")\
                .select("student_id, students(id, name), class_id, classes(name)")\
                .eq("class_id", str(class_id))\
                .is_("left_at", "null")\
                .execute()
            
            for member in (members_response.data or []):
                student_data = member.get("students", {})
                class_data = member.get("classes", {})
                
                target_students.append({
                    "homework_id": homework_id,
                    "student_id": student_data.get("id"),
                    "student_name": student_data.get("name"),
                    "class_id": str(class_id),
                    "class_name": class_data.get("name")
                })
    
    # 3. Create homework_targets snapshot
    if target_students:
        supabase_admin.table("homework_targets")\
            .insert(target_students)\
            .execute()
    
    # 4. TODO: Send Kakao notifications (optional)
    
    result = response.data[0]
    result["target_count"] = len(target_students)
    
    return result


@router.get("/", response_model=List[HomeworkResponse])
async def list_homeworks(
    current_user: TokenData = Depends(require_admin)
):
    """List all homeworks for the academy"""
    
    response = supabase_admin.table("homework")\
        .select("*")\
        .eq("academy_id", current_user.academy_id)\
        .order("created_at", desc=True)\
        .execute()
    
    homeworks = response.data or []
    
    # Get target count and class names for each homework
    for homework in homeworks:
        count_response = supabase_admin.table("homework_targets")\
            .select("id", count="exact")\
            .eq("homework_id", homework["id"])\
            .execute()
        
        homework["target_count"] = count_response.count or 0
        
        # Get unique class names
        class_ids = homework.get("class_ids", [])
        
        if class_ids:
            classes_response = supabase_admin.table("classes")\
                .select("name")\
                .in_("id", class_ids)\
                .execute()
            
            class_names = [c["name"] for c in (classes_response.data or [])]
            homework["class_names"] = class_names
        else:
            homework["class_names"] = []
    
    return homeworks


@router.get("/{homework_id}", response_model=HomeworkResponse)
async def get_homework(
    homework_id: UUID,
    current_user: TokenData = Depends(require_admin)
):
    """Get homework details"""
    
    response = supabase_admin.table("homework")\
        .select("*")\
        .eq("id", str(homework_id))\
        .eq("academy_id", current_user.academy_id)\
        .single()\
        .execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="숙제를 찾을 수 없습니다"
        )
    
    # Get target count
    count_response = supabase_admin.table("homework_targets")\
        .select("id", count="exact")\
        .eq("homework_id", str(homework_id))\
        .execute()
    
    result = response.data
    result["target_count"] = count_response.count or 0
    
    return result


@router.put("/{homework_id}", response_model=HomeworkResponse)
async def update_homework(
    homework_id: UUID,
    homework: HomeworkUpdate,
    current_user: TokenData = Depends(require_admin)
):
    """Update homework"""
    
    update_data = homework.dict(exclude_unset=True)
    
    # Convert date to string
    if update_data.get("due_date"):
        update_data["due_date"] = update_data["due_date"].isoformat()
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    response = supabase_admin.table("homework")\
        .update(update_data)\
        .eq("id", str(homework_id))\
        .eq("academy_id", current_user.academy_id)\
        .execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="숙제를 찾을 수 없습니다"
        )
    
    result = response.data[0]
    result["target_count"] = 0
    return result


@router.delete("/{homework_id}")
async def delete_homework(
    homework_id: UUID,
    current_user: TokenData = Depends(require_admin)
):
    """Delete homework"""
    
    response = supabase_admin.table("homework")\
        .delete()\
        .eq("id", str(homework_id))\
        .eq("academy_id", current_user.academy_id)\
        .execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="숙제를 찾을 수 없습니다"
        )
    
    return {"message": "숙제가 삭제되었습니다"}


# ============================================
# Admin: Submissions Management
# ============================================

@router.get("/{homework_id}/submissions")
async def list_submissions(
    homework_id: UUID,
    current_user: TokenData = Depends(require_admin)
):
    """List all submissions for a homework with target students"""
    
    # Get target students
    targets_response = supabase_admin.table("homework_targets")\
        .select("student_id, student_name, class_name")\
        .eq("homework_id", str(homework_id))\
        .execute()
    
    targets = {t["student_id"]: t for t in (targets_response.data or [])}
    
    # Get submissions
    submissions_response = supabase_admin.table("homework_submissions")\
        .select("*")\
        .eq("homework_id", str(homework_id))\
        .execute()
    
    submissions_dict = {s["student_id"]: s for s in (submissions_response.data or [])}
    
    # Get submission files
    submission_ids = [s["id"] for s in (submissions_response.data or [])]
    files_dict = {}
    
    if submission_ids:
        files_response = supabase_admin.table("submission_files")\
            .select("*")\
            .in_("submission_id", submission_ids)\
            .order("upload_order")\
            .execute()
        
        for file in (files_response.data or []):
            sid = file["submission_id"]
            if sid not in files_dict:
                files_dict[sid] = []
            files_dict[sid].append(file)
    
    # Combine targets with submissions
    results = []
    for student_id, target in targets.items():
        submission = submissions_dict.get(student_id)
        
        # Add files to submission
        if submission:
            submission["files"] = files_dict.get(submission["id"], [])
        
        results.append({
            "student_id": student_id,
            "student_name": target["student_name"],
            "class_name": target["class_name"],
            "submission": submission,
            "status": submission["status"] if submission else "pending"
        })
    
    return results


@router.put("/submissions/{submission_id}/grade")
async def grade_submission(
    submission_id: UUID,
    grade: str,
    feedback: Optional[str] = None,
    current_user: TokenData = Depends(require_admin)
):
    """Grade a homework submission"""
    
    update_data = {
        "grade": grade,
        "feedback": feedback,
        "graded_at": datetime.now(timezone.utc).isoformat(),
        "graded_by": str(current_user.user_id),
        "status": "graded"
    }
    
    response = supabase_admin.table("homework_submissions")\
        .update(update_data)\
        .eq("id", str(submission_id))\
        .execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제출을 찾을 수 없습니다"
        )
    
    return {"message": "채점이 완료되었습니다"}


# ============================================
# Student: Homework & Submissions
# ============================================

@router.get("/student/list")
async def list_student_homeworks(student_id: str):
    """
    List all homeworks assigned to a student
    (homework_targets 기반)
    """
    
    # Get assigned homeworks
    targets_response = supabase_admin.table("homework_targets")\
        .select("homework_id, homework(*)")\
        .eq("student_id", student_id)\
        .execute()
    
    homework_ids = []
    homeworks = []
    
    for target in (targets_response.data or []):
        if target.get("homework"):
            homework = target["homework"]
            homework_ids.append(homework["id"])
            homeworks.append(homework)
    
    if not homeworks:
        return []
    
    # Get student's submissions
    submissions_response = supabase_admin.table("homework_submissions")\
        .select("*")\
        .eq("student_id", student_id)\
        .in_("homework_id", homework_ids)\
        .execute()
    
    submissions_dict = {s["homework_id"]: s for s in (submissions_response.data or [])}
    
    # Get submission files
    submission_ids = [s["id"] for s in (submissions_response.data or [])]
    files_dict = {}
    
    if submission_ids:
        files_response = supabase_admin.table("submission_files")\
            .select("*")\
            .in_("submission_id", submission_ids)\
            .order("upload_order")\
            .execute()
        
        for file in (files_response.data or []):
            sid = file["submission_id"]
            if sid not in files_dict:
                files_dict[sid] = []
            files_dict[sid].append(file)
    
    # Combine homework with submission status
    for homework in homeworks:
        submission = submissions_dict.get(homework["id"])
        homework["submission"] = submission
        
        if submission:
            submission["files"] = files_dict.get(submission["id"], [])
    
    return homeworks


@router.post("/{homework_id}/submit")
async def submit_homework(
    homework_id: UUID,
    submission: HomeworkSubmissionCreate,
    student_id: str
):
    """
    Submit homework with files
    
    시퀀스:
    1. submission 저장
    2. submission_files 저장
    3. (선택) 알림톡 발송
    """
    
    # Check if homework exists and student is target
    target_response = supabase_admin.table("homework_targets")\
        .select("id")\
        .eq("homework_id", str(homework_id))\
        .eq("student_id", student_id)\
        .execute()
    
    if not target_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="숙제를 찾을 수 없거나 대상 학생이 아닙니다"
        )
    
    # Check if already submitted
    existing_response = supabase_admin.table("homework_submissions")\
        .select("id")\
        .eq("homework_id", str(homework_id))\
        .eq("student_id", student_id)\
        .execute()
    
    submission_data = {
        "homework_id": str(homework_id),
        "student_id": student_id,
        "content": submission.content,
        "status": "submitted",
        "submitted_at": datetime.now(timezone.utc).isoformat()
    }
    
    if existing_response.data:
        # Update existing submission
        submission_id = existing_response.data[0]["id"]
        
        response = supabase_admin.table("homework_submissions")\
            .update(submission_data)\
            .eq("id", submission_id)\
            .execute()
        
        # Delete old files
        supabase_admin.table("submission_files")\
            .delete()\
            .eq("submission_id", submission_id)\
            .execute()
    else:
        # Create new submission
        response = supabase_admin.table("homework_submissions")\
            .insert(submission_data)\
            .execute()
        
        submission_id = response.data[0]["id"]
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="제출에 실패했습니다"
        )
    
    # Save submission files
    if submission.files:
        file_records = []
        for idx, file_data in enumerate(submission.files):
            file_records.append({
                "submission_id": submission_id,
                "file_key": file_data.get("file_key"),
                "file_name": file_data.get("file_name"),
                "file_url": file_data.get("file_url"),
                "file_size": file_data.get("file_size"),
                "mime_type": file_data.get("mime_type", "image/jpeg"),
                "upload_order": idx
            })
        
        if file_records:
            file_insert_response = supabase_admin.table("submission_files")\
                .insert(file_records)\
                .execute()
    
    # TODO: Send Kakao notification
    
    return {
        "message": "숙제가 제출되었습니다",
        "submission_id": submission_id
    }


# ============================================
# File Upload (Presigned URL)
# ============================================

@router.post("/uploads/presign", response_model=PresignedUploadResponse)
async def create_presigned_upload(request: PresignedUploadRequest):
    """
    Generate presigned URL for file upload
    
    실제 프로덕션: S3/R2 presigned URL 생성
    현재 구현: 로컬 파일 시스템 시뮬레이션
    """
    
    import uuid
    import os
    from pathlib import Path
    
    # Generate unique file key
    file_ext = os.path.splitext(request.file_name)[1]
    file_key = f"homework/{uuid.uuid4()}{file_ext}"
    
    # 실제 프로덕션에서는:
    # - S3/R2 presigned URL 생성
    # - 시간 제한 (예: 15분)
    # - 파일 크기 제한
    
    # 현재는 로컬 경로 반환 (프론트엔드에서 FormData로 업로드)
    upload_url = f"/api/homeworks/uploads/file/{file_key}"
    public_url = f"/uploads/{file_key}"
    
    return {
        "upload_url": upload_url,
        "file_key": file_key,
        "public_url": public_url
    }


@router.post("/uploads/file/{file_key:path}")
async def upload_file(file_key: str, request: Request):
    """
    실제 파일 업로드 엔드포인트 (로컬 구현)
    
    프로덕션에서는 이 엔드포인트가 필요 없음 (S3/R2 직접 업로드)
    """
    from pathlib import Path
    
    # Read raw body
    file_data = await request.body()
    
    # Create uploads directory
    upload_dir = Path("static/uploads") / Path(file_key).parent
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = Path("static/uploads") / file_key
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    return {"message": "File uploaded successfully", "file_key": file_key}
