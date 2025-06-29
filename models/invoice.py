from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    CANCELLED = "cancelled"

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Invoice details
    invoice_number = Column(String(50), nullable=False, unique=True, index=True)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)
    
    # Status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Financial
    subtotal = Column(Integer, nullable=False, default=0)  # in cents
    tax_rate = Column(Integer, nullable=True, default=0)  # in basis points (e.g., 825 = 8.25%)
    tax_amount = Column(Integer, nullable=False, default=0)  # in cents
    total_amount = Column(Integer, nullable=False, default=0)  # in cents
    
    # Additional details
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    
    # File tracking
    pdf_path = Column(String(500), nullable=True)
    docx_path = Column(String(500), nullable=True)
    
    # Payment tracking
    paid_date = Column(DateTime, nullable=True)
    payment_method = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="invoices")
    billable_items = relationship("BillableItem", back_populates="invoice")
    invoice_items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', company_id={self.company_id})>"
    
    def calculate_totals(self):
        """Calculate and update invoice totals"""
        # Calculate subtotal from invoice items
        self.subtotal = sum(item.total_amount or 0 for item in self.invoice_items)
        
        # Calculate tax
        if self.tax_rate:
            self.tax_amount = int(self.subtotal * self.tax_rate / 10000)  # basis points to percentage
        else:
            self.tax_amount = 0
            
        # Calculate total
        self.total_amount = self.subtotal + self.tax_amount
    
    @property
    def formatted_total(self):
        """Return formatted total amount"""
        return f"${self.total_amount / 100:.2f}" 