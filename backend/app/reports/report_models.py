from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ReportResponse(BaseModel):
    id: UUID
    title: str
    file_path: str
    report_type: str
    generated_by: Optional[UUID]
    decision_case_id: Optional[UUID]
    
    class Config:
        from_attributes = True
