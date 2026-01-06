"""
Admin Dashboard API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from app.auth.utils import require_admin, TokenData
from app.database import supabase_admin

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: TokenData = Depends(require_admin)
):
    """Get admin dashboard statistics"""
    
    # Get academy info
    academy_response = supabase_admin.table("academies")\
        .select("name")\
        .eq("id", current_user.academy_id)\
        .execute()
    
    academy_name = academy_response.data[0]["name"] if academy_response.data else "알 수 없는 학원"
    
    # Get total active students count
    students_response = supabase_admin.table("students")\
        .select("id", count="exact")\
        .eq("academy_id", current_user.academy_id)\
        .eq("status", "active")\
        .execute()
    
    total_students = students_response.count or 0
    
    # Get today's attendance count
    today = datetime.utcnow().date().isoformat()
    attendance_response = supabase_admin.table("attendance")\
        .select("id", count="exact")\
        .eq("academy_id", current_user.academy_id)\
        .eq("date", today)\
        .eq("status", "present")\
        .execute()
    
    today_attendance = attendance_response.count or 0
    
    # Get this month's revenue (paid billing records)
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    billing_response = supabase_admin.table("billing")\
        .select("paid_amount")\
        .eq("academy_id", current_user.academy_id)\
        .eq("status", "paid")\
        .gte("paid_at", first_day_of_month.date().isoformat())\
        .execute()
    
    monthly_revenue = sum(record.get("paid_amount", 0) for record in (billing_response.data or []))
    
    # Get recent activity (last 10 records)
    # Combine different activities: student registrations, attendance, payments
    recent_activity = []
    
    # Recent student registrations
    recent_students = supabase_admin.table("students")\
        .select("name, created_at")\
        .eq("academy_id", current_user.academy_id)\
        .order("created_at", desc=True)\
        .limit(3)\
        .execute()
    
    for student in (recent_students.data or []):
        created_at = datetime.fromisoformat(student["created_at"].replace('Z', '+00:00'))
        time_ago = get_time_ago(created_at)
        recent_activity.append({
            "id": f"student_{student['name']}_{created_at.timestamp()}",
            "icon": "user-plus",
            "title": f"{student['name']} 학생이 등록되었습니다",
            "time": time_ago,
            "timestamp": created_at.timestamp()
        })
    
    # Recent attendance (today)
    recent_attendance = supabase_admin.table("attendance")\
        .select("students!inner(name), check_in_time")\
        .eq("academy_id", current_user.academy_id)\
        .eq("date", today)\
        .eq("status", "present")\
        .order("check_in_time", desc=True)\
        .limit(3)\
        .execute()
    
    for att in (recent_attendance.data or []):
        if att.get("check_in_time"):
            check_in = datetime.fromisoformat(att["check_in_time"].replace('Z', '+00:00'))
            time_ago = get_time_ago(check_in)
            recent_activity.append({
                "id": f"attendance_{att['students']['name']}_{check_in.timestamp()}",
                "icon": "check-circle",
                "title": f"{att['students']['name']} 학생이 출석했습니다",
                "time": time_ago,
                "timestamp": check_in.timestamp()
            })
    
    # Recent payments
    recent_payments = supabase_admin.table("billing")\
        .select("students!inner(name), paid_at")\
        .eq("academy_id", current_user.academy_id)\
        .eq("status", "paid")\
        .order("paid_at", desc=True)\
        .limit(3)\
        .execute()
    
    for payment in (recent_payments.data or []):
        if payment.get("paid_at"):
            paid_at = datetime.fromisoformat(payment["paid_at"].replace('Z', '+00:00') if 'Z' in payment["paid_at"] else payment["paid_at"])
            time_ago = get_time_ago(paid_at)
            recent_activity.append({
                "id": f"payment_{payment['students']['name']}_{paid_at.timestamp()}",
                "icon": "credit-card",
                "title": f"{payment['students']['name']} 학생 결제 확인",
                "time": time_ago,
                "timestamp": paid_at.timestamp()
            })
    
    # Sort by timestamp and take top 10
    recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_activity = recent_activity[:10]
    
    # Remove timestamp from response
    for activity in recent_activity:
        del activity["timestamp"]
    
    return {
        "academy_name": academy_name,
        "stats": {
            "totalStudents": total_students,
            "todayAttendance": today_attendance,
            "monthlyRevenue": monthly_revenue
        },
        "recent_activity": recent_activity
    }


def get_time_ago(dt: datetime) -> str:
    """Convert datetime to relative time string"""
    now = datetime.utcnow().replace(tzinfo=dt.tzinfo)
    delta = now - dt
    
    if delta.days > 0:
        return f"{delta.days}일 전"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours}시간 전"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes}분 전"
    else:
        return "방금 전"

