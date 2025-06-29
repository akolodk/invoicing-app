# Configuration file for Invoice Generator
# Copy this file to config.py and modify as needed

import os

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/invoicing.db")

# Directory Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
GENERATED_DIR = os.getenv("GENERATED_DIR", "./generated")
TEMPLATES_DIR = os.getenv("TEMPLATES_DIR", "./templates")

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Invoice Settings
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "USD")
DEFAULT_TAX_RATE = float(os.getenv("DEFAULT_TAX_RATE", "0.0"))
DEFAULT_PAYMENT_TERMS_DAYS = int(os.getenv("DEFAULT_PAYMENT_TERMS_DAYS", "30"))

# Company Information (for invoice headers)
COMPANY_INFO = {
    "name": os.getenv("COMPANY_NAME", "Your Business Name"),
    "email": os.getenv("COMPANY_EMAIL", "billing@yourbusiness.com"),
    "phone": os.getenv("COMPANY_PHONE", "+1 555-123-4567"),
    "address": os.getenv("COMPANY_ADDRESS", "123 Business Street, Suite 100"),
    "city": os.getenv("COMPANY_CITY", "Your City"),
    "state": os.getenv("COMPANY_STATE", "YS"),
    "zip": os.getenv("COMPANY_ZIP", "12345"),
    "country": os.getenv("COMPANY_COUNTRY", "USA"),
    "website": os.getenv("COMPANY_WEBSITE", "https://yourbusiness.com"),
    "tax_id": os.getenv("COMPANY_TAX_ID", "12-3456789"),
}

# Supported file types for import
SUPPORTED_FILE_TYPES = ['.csv', '.xlsx', '.xls']

# Invoice numbering format
INVOICE_NUMBER_FORMAT = "INV-{year}{month:02d}{day:02d}-{sequence:03d}"

# PDF Generation Settings
PDF_SETTINGS = {
    "page_size": "A4",
    "margin_top": 72,
    "margin_bottom": 72,
    "margin_left": 72,
    "margin_right": 72,
    "show_logo": True,
    "logo_height": 50,
}

# Email Settings (for sending invoices)
EMAIL_SETTINGS = {
    "smtp_server": os.getenv("SMTP_SERVER", ""),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "smtp_username": os.getenv("SMTP_USERNAME", ""),
    "smtp_password": os.getenv("SMTP_PASSWORD", ""),
    "use_tls": os.getenv("SMTP_USE_TLS", "True").lower() == "true",
} 