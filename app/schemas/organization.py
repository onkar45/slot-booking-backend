from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
import re


class OrganizationCreate(BaseModel):
    name: str
    subdomain: str

    @field_validator('subdomain')
    @classmethod
    def validate_subdomain(cls, v):
        v = v.lower().strip()
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Subdomain can only contain lowercase letters, numbers, and hyphens')
        if len(v) < 2:
            raise ValueError('Subdomain must be at least 2 characters')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Organization name must be at least 2 characters')
        return v.strip()


class OrganizationResponse(BaseModel):
    id: int
    name: str
    subdomain: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationWithAdminResponse(BaseModel):
    id: int
    name: str
    subdomain: str
    is_active: bool
    created_at: datetime
    admin_email: Optional[str] = None
    admin_name: Optional[str] = None

    class Config:
        from_attributes = True
