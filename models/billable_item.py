from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class BillableItem(Base):
    __tablename__ = "billable_items"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Work details
    description = Column(Text, nullable=False)
    project = Column(String(255), nullable=True)
    task_category = Column(String(100), nullable=True)
    
    # Time tracking
    date_worked = Column(DateTime, nullable=False)
    hours = Column(Numeric(precision=5, scale=2), nullable=False)  # e.g., 1.5 hours
    
    # Financial
    hourly_rate = Column(Integer, nullable=True)  # in cents, overrides company default
    total_amount = Column(Integer, nullable=True)  # in cents, calculated field
    
    # Invoice tracking
    is_invoiced = Column(Boolean, default=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    
    # Import tracking
    import_source = Column(String(255), nullable=True)  # filename if imported
    import_date = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="billable_items")
    invoice = relationship("Invoice", back_populates="billable_items")

    def __repr__(self):
        return f"<BillableItem(id={self.id}, company_id={self.company_id}, hours={self.hours})>"
    
    @property
    def calculated_amount(self):
        """Calculate total amount based on hours and rate"""
        if self.hourly_rate and self.hours:
            return int(float(self.hours) * self.hourly_rate)
        elif self.company and self.company.default_hourly_rate and self.hours:
            return int(float(self.hours) * self.company.default_hourly_rate)
        return 0
    
    def update_total_amount(self):
        """Update the stored total amount"""
        if self.hourly_rate and self.hours:
            self.total_amount = int(float(self.hours) * self.hourly_rate)
        elif self.company and self.company.default_hourly_rate and self.hours:
            self.total_amount = int(float(self.hours) * self.company.default_hourly_rate)
        else:
            self.total_amount = 0 