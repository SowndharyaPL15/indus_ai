import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, ForeignKey, Enum
import enum
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import BaseModel

class SeverityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class MaintenanceRecord(BaseModel):
    __tablename__ = "maintenance_records"
    machine_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("machines.id"), index=True)
    technician_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String)

class Incident(BaseModel):
    __tablename__ = "incidents"
    machine_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=True, index=True)
    severity: Mapped[SeverityEnum] = mapped_column(Enum(SeverityEnum))
    description: Mapped[str] = mapped_column(Text)

class InspectionReport(BaseModel):
    __tablename__ = "inspection_reports"
    inspector_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    machine_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=True, index=True)
    findings: Mapped[str] = mapped_column(Text)
