# Polish Invoice Generator (Generowanie Polskich Faktur)

This invoicing application now supports generating Polish invoices (Faktury) that comply with Polish accounting standards and requirements.

## Features / Funkcje

### Polish Invoice Format Includes:
- **Proper Polish layout** with seller (Sprzedawca) and buyer (Nabywca) sections
- **VAT calculations** with standard Polish VAT rates
- **Polish language labels** and formatting
- **NIP and REGON numbers** for proper tax identification
- **Polish date format** (DD.MM.YYYY)
- **Signature sections** for authorized persons
- **Bank account information** for payments

### Key Polish Invoice Elements:
- Faktura title and number
- Issue date (Data wystawienia) and sale date (Data sprzedaży)
- Payment term (Termin płatności)
- Seller information with NIP and REGON
- Detailed items table with VAT breakdown
- Summary with net value, VAT, and total amount
- Payment information

## Configuration / Konfiguracja

### Method 1: Environment Variables
Set these environment variables to configure your Polish company information:

```bash
# Company Information
export POLISH_COMPANY_NAME="MAGDALENA KOŁODKIEWICZ BRIGHT"
export POLISH_COMPANY_TYPE="COACHING SZKOLENIA DORADZTWO HR"
export POLISH_COMPANY_ADDRESS="ul. Obrzetska 1a/118"
export POLISH_COMPANY_CITY="02-691 Warszawa"
export POLISH_COMPANY_NIP="7281339661"
export POLISH_COMPANY_REGON=""
export POLISH_COMPANY_PHONE=""
export POLISH_COMPANY_EMAIL=""

# Header/Branding Information
export POLISH_HEADER_TITLE="bright"
export POLISH_HEADER_SUBTITLE="ways to grow"
export POLISH_HEADER_DESC="coaching, szkolenia, doradztwo HR"

# Bank Information
export POLISH_COMPANY_BANK="64 1140 2004 0000 3202 3382 6537"
export POLISH_COMPANY_BANK_NAME="BRE BANK SA"

# Invoice Settings
export POLISH_DEFAULT_VAT_RATE="23.0"
export POLISH_PAYMENT_TERMS_DAYS="14"
export POLISH_PAYMENT_METHOD="Przelew bankowy"
```

### Method 2: Configuration File
Edit the file `config/polish_invoice_config.py` to modify the default values directly.

### Method 3: UI Settings
Use the Settings page in the application to configure your Polish company information through the user interface.

## Usage / Użycie

1. **Add Companies**: Make sure to add the buyer's company information, including their NIP number in the "Tax ID" field.

2. **Generate Invoice**: 
   - Go to "Generate Invoice" page
   - Select "Polish (Faktura)" from the "Invoice Language" dropdown
   - Set the VAT rate (default is 23% - standard Polish VAT)
   - Select "PLN" as currency
   - Fill in other invoice details
   - Click "Generate Invoice"

3. **Download**: The generated Polish invoice will be available as a PDF download.

## Polish Invoice Requirements / Wymagania Polskich Faktur

This generator follows Polish invoice requirements including:

- **Mandatory information**: Invoice number, dates, seller and buyer details
- **VAT compliance**: Proper VAT calculations and rates
- **Tax identification**: NIP numbers for both seller and buyer
- **Format compliance**: Standard Polish invoice layout
- **Language**: All labels and descriptions in Polish

## Sample Invoice Elements / Przykładowe Elementy Faktury

The generated invoice includes:

```
                                                     bright
                                               ways to grow
coaching, szkolenia, doradztwo HR

FAKTURA

                                          Faktura VAT nr INV-20240628-001/oryginał
                                                        28 czerwca 2024

Sprzedawca:                           Nabywca:
MAGDALENA KOŁODKIEWICZ BRIGHT         FIRMA KLIENTA SP. Z O.O.
COACHING SZKOLENIA DORADZTWO HR       ul. Klienta 456
02-691 Warszawa, ul. Obrzetska 1a/118  01-001 Kraków
NIP: 7281339661                       NIP: 987-654-32-10
Bank: BRE BANK SA Nr rachunku: 64 1140 2004 0000 3202 3382 6537
```

## Customization / Dostosowanie

You can customize:
- Company information
- Default VAT rates
- Payment terms
- Bank account information
- Invoice labels and formatting

## Support / Wsparcie

For issues or customization requests related to Polish invoices, please check:
1. Your company configuration in Settings
2. Environment variables setup
3. Configuration file values

The Polish invoice generator is designed to be compliant with Polish accounting standards, but please consult with your accountant to ensure it meets your specific business requirements. 