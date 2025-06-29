from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Business details
    tax_id = Column(String(50), nullable=True)
    contact_person = Column(String(255), nullable=True)
    
    # Settings
    default_hourly_rate = Column(Integer, nullable=True)  # in cents
    currency = Column(String(3), default="USD")
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    billable_items = relationship("BillableItem", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"
    
    @property
    def formatted_address(self):
        """Return formatted address string"""
        address_parts = [
            self.address,
            self.city,
            f"{self.state} {self.zip_code}" if self.state and self.zip_code else self.state or self.zip_code,
            self.country
        ]
        return ", ".join(filter(None, address_parts)) 