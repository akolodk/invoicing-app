# Polish Invoice Configuration
# Configuration for Polish invoice generation (Faktura)

import os

# Polish Company Information (Seller/Sprzedawca)
POLISH_SELLER_INFO = {
    "name": os.getenv("POLISH_COMPANY_NAME", "MAGDALENA KOŁODKIEWICZ BRIGHT"),
    "business_type": os.getenv("POLISH_COMPANY_TYPE", "COACHING SZKOLENIA DORADZTWO HR"),
    "address": os.getenv("POLISH_COMPANY_ADDRESS", "ul. Obrzetska 1a/118"),
    "city": os.getenv("POLISH_COMPANY_CITY", "02-691 Warszawa"),
    "nip": os.getenv("POLISH_COMPANY_NIP", "7281339661"),
    "regon": os.getenv("POLISH_COMPANY_REGON", ""),
    "phone": os.getenv("POLISH_COMPANY_PHONE", ""),
    "email": os.getenv("POLISH_COMPANY_EMAIL", ""),
    "bank_account": os.getenv("POLISH_COMPANY_BANK", "64 1140 2004 0000 3202 3382 6537"),
    "bank_name": os.getenv("POLISH_COMPANY_BANK_NAME", "BRE BANK SA"),
    "header_title": os.getenv("POLISH_HEADER_TITLE", "bright"),
    "header_subtitle": os.getenv("POLISH_HEADER_SUBTITLE", "ways to grow"),
    "header_description": os.getenv("POLISH_HEADER_DESC", "coaching, szkolenia, doradztwo HR")
}

# Polish Invoice Settings
POLISH_INVOICE_SETTINGS = {
    "default_vat_rate": float(os.getenv("POLISH_DEFAULT_VAT_RATE", "23.0")),  # Standard Polish VAT rate
    "currency": "PLN",
    "date_format": "%d.%m.%Y",
    "payment_method": os.getenv("POLISH_PAYMENT_METHOD", "Przelew bankowy"),
    "default_payment_terms_days": int(os.getenv("POLISH_PAYMENT_TERMS_DAYS", "14")),
}

# Polish Invoice Labels/Translations
POLISH_LABELS = {
    "invoice_title": "FAKTURA",
    "invoice_number": "Nr faktury:",
    "issue_date": "Data wystawienia:",
    "sale_date": "Data sprzedaży:",
    "payment_date": "Termin płatności:",
    "seller": "SPRZEDAWCA:",
    "buyer": "NABYWCA:",
    "items_header": "POZYCJE FAKTURY:",
    "item_no": "Lp.",
    "description": "Nazwa towaru/usługi",
    "quantity": "Ilość",
    "unit": "J.m.",
    "net_price": "Cena netto",
    "vat_rate": "VAT %",
    "vat_amount": "Kwota VAT",
    "gross_amount": "Wartość brutto",
    "total": "RAZEM:",
    "summary": "PODSUMOWANIE:",
    "net_value": "Wartość netto:",
    "vat_value": "VAT:",
    "to_pay": "Do zapłaty:",
    "payment_method": "Sposób płatności:",
    "payment_term": "Termin płatności:",
    "notes": "Uwagi:",
    "signature_issuer": "Osoba upoważniona do wystawienia faktury",
    "signature_recipient": "Osoba upoważniona do odbioru faktury",
    "signature": "podpis",
    "unit_hour": "godz.",
    "unit_piece": "szt.",
    "unit_service": "usł.",
    "generated_on": "Faktura wygenerowana:",
    "nip": "NIP:",
    "regon": "REGON:",
    "phone": "Tel:",
    "email": "Email:",
    "bank_account": "Nr konta:",
    "not_specified": "Nie określono",
    "not_provided": "Nie podano"
}

# Helper function to get seller info
def get_polish_seller_info():
    """Get Polish seller information from configuration"""
    return POLISH_SELLER_INFO.copy()

# Helper function to get Polish labels
def get_polish_labels():
    """Get Polish labels/translations"""
    return POLISH_LABELS.copy()

# Helper function to get Polish invoice settings
def get_polish_invoice_settings():
    """Get Polish invoice settings"""
    return POLISH_INVOICE_SETTINGS.copy() 