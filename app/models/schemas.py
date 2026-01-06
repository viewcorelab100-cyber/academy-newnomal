"""
Pydantic Models for Request/Response
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID


# ============================================
# Auth Models
# ============================================
class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class AdminRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    academy_id: UUID


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str
    academy_id: str
    role: str  # 'admin', 'student'


# ============================================
# Academy Models
# ============================================
class AcademyCreate(BaseModel):
    name: str
    code: str
    owner_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None


class AcademyResponse(BaseModel):
    id: UUID
    name: str
    code: str
    owner_name: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    address: Optional[str]
    created_at: datetime


# ============================================
# Feature Library Models
# ============================================
class FeatureInfo(BaseModel):
    code: str
    name: str
    description: str
    icon: str
    category: str


class AcademyFeatureResponse(BaseModel):
    id: UUID
    academy_id: UUID
    feature_code: str
    enabled: bool
    enabled_at: Optional[datetime]
    settings: dict = {}


class FeatureToggle(BaseModel):
    feature_code: str
    enabled: bool


# ============================================
# Student Models
# ============================================
class StudentCreate(BaseModel):
    name: str
    student_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    grade: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_name: Optional[str] = None
    memo: Optional[str] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    grade: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_name: Optional[str] = None
    status: Optional[str] = None
    memo: Optional[str] = None


class StudentResponse(BaseModel):
    id: UUID
    academy_id: UUID
    name: str
    student_number: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    grade: Optional[str]
    parent_phone: Optional[str]
    parent_name: Optional[str]
    is_linked: bool
    invite_token: Optional[str]
    status: str
    created_at: datetime


class StudentInviteResponse(BaseModel):
    invite_link: str
    qr_code_data: str
    expires_at: datetime
    student_name: str


# ============================================
# OAuth & User Account Models
# ============================================
class UserAccountResponse(BaseModel):
    id: UUID
    provider: str
    provider_user_id: str
    email: Optional[str]
    name: Optional[str]
    created_at: datetime


class StudentLinkResponse(BaseModel):
    id: UUID
    student_id: UUID
    user_account_id: UUID
    linked_at: datetime


# ============================================
# Attendance Models
# ============================================
class AttendanceCheckIn(BaseModel):
    qr_code: str


class AttendanceCheckOut(BaseModel):
    qr_code: str


class AttendanceManualCreate(BaseModel):
    student_id: UUID
    date: date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: str = "present"
    memo: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: UUID
    student_id: UUID
    student_name: Optional[str] = None
    date: date
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    status: str
    check_in_method: Optional[str]
    check_out_method: Optional[str]
    memo: Optional[str]


# ============================================
# Billing Models
# ============================================
class BillingCreate(BaseModel):
    student_id: UUID
    billing_date: date
    due_date: Optional[date] = None
    amount: int
    title: str
    description: Optional[str] = None


class BillingUpdate(BaseModel):
    paid_amount: Optional[int] = None
    status: Optional[str] = None
    payment_method: Optional[str] = None
    paid_at: Optional[datetime] = None
    memo: Optional[str] = None


class BillingResponse(BaseModel):
    id: UUID
    student_id: UUID
    student_name: Optional[str] = None
    billing_date: date
    due_date: Optional[date]
    amount: int
    paid_amount: int
    status: str
    title: str
    description: Optional[str]
    payment_method: Optional[str]
    paid_at: Optional[datetime]
    created_at: datetime


# ============================================
# Homework Models
# ============================================
class HomeworkCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    class_ids: List[UUID] = []  # 대상 반 목록


class HomeworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    subject: Optional[str] = None
    grade_level: Optional[str] = None


class HomeworkResponse(BaseModel):
    id: UUID
    academy_id: UUID
    title: str
    description: Optional[str]
    due_date: Optional[date]
    subject: Optional[str]
    grade_level: Optional[str]
    class_ids: Optional[List[UUID]] = []
    created_at: datetime
    target_count: Optional[int] = 0  # 대상 학생 수
    class_names: Optional[List[str]] = []  # 반 이름 목록


class HomeworkSubmissionCreate(BaseModel):
    content: Optional[str] = None
    files: List[Dict] = []  # [{file_key, file_name, file_url, file_size}]


class HomeworkSubmissionUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None


class HomeworkSubmissionResponse(BaseModel):
    id: UUID
    homework_id: UUID
    student_id: UUID
    status: str
    submitted_at: Optional[datetime]
    content: Optional[str]
    grade: Optional[str]
    feedback: Optional[str]
    files: Optional[List[Dict]] = []  # 제출 파일 목록


# ============================================
# Notice Models
# ============================================
class NoticeCreate(BaseModel):
    title: str
    content: str
    is_important: bool = False
    is_pinned: bool = False
    target_audience: str = "all"


class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_important: Optional[bool] = None
    is_pinned: Optional[bool] = None


class NoticeResponse(BaseModel):
    id: UUID
    academy_id: UUID
    title: str
    content: str
    is_important: bool
    is_pinned: bool
    target_audience: str
    view_count: int
    published_at: datetime
    created_at: datetime


# ============================================
# Counseling Models
# ============================================
class CounselingCreate(BaseModel):
    student_id: UUID
    counseling_date: date
    duration: Optional[int] = None
    type: Optional[str] = None
    topic: Optional[str] = None
    content: str
    action_items: Optional[str] = None
    is_confidential: bool = False


class CounselingUpdate(BaseModel):
    counseling_date: Optional[date] = None
    duration: Optional[int] = None
    type: Optional[str] = None
    topic: Optional[str] = None
    content: Optional[str] = None
    action_items: Optional[str] = None
    is_confidential: Optional[bool] = None


class CounselingResponse(BaseModel):
    id: UUID
    student_id: UUID
    student_name: Optional[str] = None
    counselor_id: Optional[UUID]
    counseling_date: date
    duration: Optional[int]
    type: Optional[str]
    topic: Optional[str]
    content: str
    action_items: Optional[str]
    is_confidential: bool
    created_at: datetime


# ============================================
# QR Code Models
# ============================================
class QRCodeCreate(BaseModel):
    type: str = "attendance"
    expires_at: Optional[datetime] = None


class QRCodeResponse(BaseModel):
    id: UUID
    code: str
    type: str
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime


# ============================================
# Class Models (반 관리)
# ============================================
class ClassCreate(BaseModel):
    name: str
    grade_level: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    teacher_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    grade_level: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ClassResponse(BaseModel):
    id: UUID
    academy_id: UUID
    name: str
    grade_level: Optional[str]
    subject: Optional[str]
    description: Optional[str]
    is_active: bool
    student_count: Optional[int] = 0  # 소속 학생 수
    created_at: datetime


class ClassMemberAdd(BaseModel):
    student_ids: List[UUID]


# ============================================
# File Upload Models
# ============================================
class PresignedUploadRequest(BaseModel):
    file_name: str
    content_type: str = "image/jpeg"


class PresignedUploadResponse(BaseModel):
    upload_url: str
    file_key: str
    public_url: str


class SubmissionFileResponse(BaseModel):
    id: UUID
    file_key: str
    file_name: str
    file_url: str
    file_size: Optional[int]
    mime_type: Optional[str]
    upload_order: int
    created_at: datetime


# ============================================
# Notice Models (공지사항)
# ============================================
class NoticeAttachment(BaseModel):
    """공지 첨부파일"""
    file_key: str
    file_name: str
    file_url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class NoticeCreate(BaseModel):
    """공지 생성"""
    title: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)
    class_ids: List[UUID] = Field(..., min_items=1)
    status: Optional[str] = "draft"  # 'draft' or 'published'
    attachments: Optional[List[NoticeAttachment]] = []


class NoticeUpdate(BaseModel):
    """공지 수정"""
    title: Optional[str] = None
    body: Optional[str] = None
    class_ids: Optional[List[UUID]] = None
    status: Optional[str] = None


class NoticeResponse(BaseModel):
    """공지 응답"""
    id: UUID
    academy_id: UUID
    title: str
    body: str
    status: str
    published_at: Optional[datetime]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    target_count: Optional[int] = 0  # 대상 반 수
    attachment_count: Optional[int] = 0  # 첨부파일 수


class NoticeDetailResponse(NoticeResponse):
    """공지 상세 (대상 반 + 첨부파일 포함)"""
    target_classes: Optional[List[Dict[str, Any]]] = []
    attachments: Optional[List[Dict[str, Any]]] = []

