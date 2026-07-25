import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Enum
from app.db.base import BaseModel


class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    MAINTENANCE_ENGINEER = "MAINTENANCE_ENGINEER"
    SAFETY_OFFICER = "SAFETY_OFFICER"
    QUALITY_ENGINEER = "QUALITY_ENGINEER"
    PLANT_MANAGER = "PLANT_MANAGER"
    AUDITOR = "AUDITOR"
    FIELD_TECHNICIAN = "FIELD_TECHNICIAN"


class User(BaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), default=RoleEnum.FIELD_TECHNICIAN)
    department: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    decision_cases = relationship("DecisionCase", back_populates="user")
