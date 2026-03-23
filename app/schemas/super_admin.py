from pydantic import BaseModel, EmailStr
from datetime import datetime, date, time
from typing import Optional, List


class CreateOrgAdmin(BaseModel):
    name: str
    email: EmailStr
    password: str


class OrgAdminResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    organization_id: Optional[int]

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_users: int
    total_bookings: int
    approved_bookings: int
    pending_bookings: int


class CompanyAnalytics(BaseModel):
    company_name: str
    total_bookings: int
    approved_bookings: int
    pending_bookings: int


class UserBasicInfo(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class OrgBasicInfo(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True


class LoginActivityResponse(BaseModel):
    id: int
    user_id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    login_time: datetime
    user: Optional[UserBasicInfo] = None
    organization: Optional[OrgBasicInfo] = None

    class Config:
        from_attributes = True


class BookingUserInfo(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class SuperAdminBookingResponse(BaseModel):
    id: int
    user_id: int
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: str
    description: Optional[str] = None
    company_name: Optional[str] = None
    hr_name: Optional[str] = None
    mobile_number: Optional[str] = None
    email_id: Optional[str] = None
    created_at: datetime
    user: Optional[BookingUserInfo] = None

    class Config:
        from_attributes = True
