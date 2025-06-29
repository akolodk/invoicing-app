# Vibe coding experiment 
# not a single line of code in this repo was written by a real person.

# Invoice Generator

A comprehensive invoicing application built with Python and Streamlit for managing billable hours and generating professional invoices.

## Features

- 🏢 **Multi-Company Support**: Manage multiple client companies with detailed information
- ⏰ **Time Tracking**: Track billable hours with project and task categorization
- 📁 **File Import**: Import billable hours from CSV and Excel files
- 📄 **Invoice Generation**: Create professional PDF and Word invoices
- 💰 **Financial Management**: Track payments, taxes, and revenue
- 🎨 **Customizable Templates**: Configurable invoice headers and branding
- 🐳 **Docker Ready**: Easy deployment with Docker containers

## Quick Start

### Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.11+ with pip

### Option 1: Docker Deployment (Recommended)

1. **Clone and navigate to the project**:
   ```bash
   cd work/invoicing-app
   ```

2. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   Open your browser and go to `http://localhost:8501`

### Option 2: Local Python Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   streamlit run app.py
   ```

3. **Access the application**:
   Open your browser and go to `http://localhost:8501`

## Usage Guide

### 1. Setup Companies

- Navigate to the **Companies** page
- Add your client companies with contact information
- Set default hourly rates for each company
- Configure billing addresses and tax information

### 2. Track Billable Hours

**Manual Entry:**
- Go to **Billable Items** page
- Add individual work entries with descriptions, hours, and dates
- Categorize work by project and task type

**File Import:**
- Go to **Import Data** page
- Upload CSV or Excel files with billable hours
- Map file columns to required fields
- Review and import the data

### 3. Generate Invoices

- Navigate to **Generate Invoice** page
- Select a company and date range
- Review billable items to include
- Add invoice details (number, terms, notes)
- Generate PDF or Word document

### 4. Configure Settings

- Upload company logo
- Set default invoice templates
- Configure tax rates and payment terms
- Customize invoice branding

## File Import Format

### Required Columns
- `description`: Description of work performed
- `date_worked`: Date the work was performed (YYYY-MM-DD)
- `hours`: Number of hours worked (decimal format)

### Optional Columns
- `project`: Project name or identifier
- `task_category`: Type of work (Development, Design, etc.)
- `hourly_rate`: Override default hourly rate

### Example CSV Format
```csv
date_worked,description,hours,project,task_category,hourly_rate
2024-01-15,"Frontend development for login page",3.5,"Project Alpha","Development",75.00
2024-01-16,"Database schema design",2.0,"Project Alpha","Architecture",85.00
2024-01-17,"Client meeting and requirements review",1.5,"Project Alpha","Consultation",100.00
```

## Database Schema

The application uses SQLite for local storage with the following main tables:

- **companies**: Client company information
- **billable_items**: Individual work entries
- **invoices**: Invoice headers and metadata
- **invoice_items**: Invoice line items

## Development

### Project Structure
```
invoicing-app/
├── app.py                 # Main Streamlit application
├── models/               # Database models
│   ├── __init__.py
│   ├── database.py       # Database configuration
│   ├── company.py        # Company model
│   ├── billable_item.py  # Billable item model
│   ├── invoice.py        # Invoice model
│   └── invoice_item.py   # Invoice item model
├── services/            # Business logic
│   ├── __init__.py
│   ├── file_import.py   # File import service
│   ├── invoice_generator.py  # Invoice generation
│   ├── company_service.py    # Company management
│   └── billable_service.py   # Billable items management
├── templates/           # Invoice templates
├── data/               # SQLite database
├── uploads/            # Uploaded files
├── generated/          # Generated invoices
├── config/             # Configuration files
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
└── README.md          # This file
```

### Adding New Features

1. **Database Changes**: Modify models in `models/` directory
2. **Business Logic**: Add services in `services/` directory
3. **UI Components**: Update `app.py` with new Streamlit components
4. **Templates**: Add invoice templates in `templates/` directory

## Configuration

### Environment Variables

- `DATABASE_URL`: Database connection string (default: SQLite)
- `UPLOAD_DIR`: Directory for uploaded files (default: ./uploads)
- `GENERATED_DIR`: Directory for generated invoices (default: ./generated)

### Docker Volumes

The Docker setup includes persistent volumes for:
- `./data`: Database and application data
- `./uploads`: Uploaded files
- `./generated`: Generated invoices
- `./config`: Configuration files

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Ensure the `data` directory exists and is writable
   - Check SQLite file permissions

2. **File Import Errors**:
   - Verify CSV/Excel file format
   - Check column names and data types
   - Ensure dates are in YYYY-MM-DD format

3. **Docker Issues**:
   - Ensure Docker is running
   - Check port 8501 is available
   - Verify Docker Compose version compatibility

### Logs

- **Docker logs**: `docker-compose logs invoicing-app`
- **Application logs**: Check Streamlit console output

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues and feature requests, please create an issue in the project repository. 
