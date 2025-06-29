from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .database import Base

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Line item details
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(precision=10, scale=2), nullable=False, default=1)
    unit_price = Column(Integer, nullable=False)  # in cents
    total_amount = Column(Integer, nullable=False)  # in cents
    
    # Optional details
    project = Column(String(255), nullable=True)
    task_category = Column(String(100), nullable=True)
    
    # Line ordering
    line_order = Column(Integer, nullable=False, default=0)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="invoice_items")

    def __repr__(self):
        return f"<InvoiceItem(id={self.id}, invoice_id={self.invoice_id}, description='{self.description[:50]}')>"
    
    def calculate_total(self):
        """Calculate and update total amount"""
        self.total_amount = int(float(self.quantity) * self.unit_price)
    
    @property
    def formatted_unit_price(self):
        """Return formatted unit price"""
        return f"${self.unit_price / 100:.2f}"
    
    @property
    def formatted_total(self):
        """Return formatted total amount"""
        return f"${self.total_amount / 100:.2f}" 