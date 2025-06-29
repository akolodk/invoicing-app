import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Invoice Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first run
@st.cache_resource
def init_database():
    """Initialize database connection and tables"""
    try:
        from models.database import init_db
        init_db()
        return True
    except Exception as e:
        st.error(f"Database initialization failed: {str(e)}")
        return False

def generate_unique_invoice_number():
    """Generate a unique invoice number by checking existing ones"""
    try:
        from models.database import SessionLocal
        from models.invoice import Invoice
        
        db = SessionLocal()
        today = datetime.now().strftime('%Y%m%d')
        base_number = f"INV-{today}"
        
        # Find existing invoices with the same date pattern
        existing_numbers = db.query(Invoice.invoice_number).filter(
            Invoice.invoice_number.like(f"{base_number}%")
        ).all()
        
        # Extract the counter part and find the highest
        counters = []
        for (number,) in existing_numbers:
            try:
                # Extract the last part after the last dash
                counter_part = number.split('-')[-1]
                if counter_part.isdigit():
                    counters.append(int(counter_part))
            except:
                continue
        
        # Generate next number
        next_counter = max(counters) + 1 if counters else 1
        unique_number = f"{base_number}-{next_counter:03d}"
        
        db.close()
        return unique_number
        
    except Exception as e:
        # Fallback to timestamp-based number if there's an error
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"INV-{timestamp}"

def main():
    """Main application function"""
    st.title("Invoice Generator")
    st.write("Welcome to the Invoice Generator!")
    
    # Initialize database
    if not init_database():
        st.stop()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Dashboard", "Companies", "Billable Items", "Import Data", "Generate Invoice", "Settings"]
        )
    
    # Route to different pages
    if page == "Dashboard":
        show_dashboard()
    elif page == "Companies":
        show_companies()
    elif page == "Billable Items":
        show_billable_items()
    elif page == "Import Data":
        show_import_data()
    elif page == "Generate Invoice":
        show_generate_invoice()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    """Display dashboard with overview statistics"""
    st.header("📊 Dashboard")
    
    try:
        from models.database import SessionLocal
        from models.company import Company
        from models.billable_item import BillableItem
        from models.invoice import Invoice
        from sqlalchemy.orm import joinedload
        
        # Get data from database
        db = SessionLocal()
        
        # Count companies
        total_companies = db.query(Company).filter(Company.is_active == True).count()
        
        # Calculate unbilled hours and amount (with eager loading)
        unbilled_items = db.query(BillableItem).options(joinedload(BillableItem.company)).filter(BillableItem.is_invoiced == False).all()
        unbilled_hours = sum(float(item.hours) for item in unbilled_items)
        
        # Calculate amount while session is active
        for item in unbilled_items:
            if not item.total_amount:
                item.update_total_amount()
        
        unbilled_amount = sum(item.total_amount or 0 for item in unbilled_items) / 100  # Convert from cents
        
        # Total revenue (all invoiced items)
        invoiced_items = db.query(BillableItem).options(joinedload(BillableItem.company)).filter(BillableItem.is_invoiced == True).all()
        
        # Calculate amount while session is active
        for item in invoiced_items:
            if not item.total_amount:
                item.update_total_amount()
        
        total_revenue = sum(item.total_amount or 0 for item in invoiced_items) / 100  # Convert from cents
        
        # Pending invoices (this will be 0 for now since we haven't implemented invoicing yet)
        pending_invoices = 0
        
        db.close()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Companies", total_companies)
        
        with col2:
            st.metric("Unbilled Hours", f"{unbilled_hours:.1f}")
        
        with col3:
            st.metric("Unbilled Revenue", f"${unbilled_amount:.2f}")
        
        with col4:
            st.metric("Total Revenue", f"${total_revenue:.2f}")
        
        st.markdown("---")
        
        # Recent activity
        st.subheader("Recent Activity")
        
        if unbilled_items:
            # Show recent unbilled items
            recent_items = sorted(unbilled_items, key=lambda x: x.created_at or x.date_worked, reverse=True)[:5]
            
            for item in recent_items:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{item.company.name}** - {item.description[:40]}{'...' if len(item.description) > 40 else ''}")
                    with col2:
                        st.write(f"{item.hours}h on {item.date_worked.strftime('%Y-%m-%d')}")
                    with col3:
                        st.write(f"${(item.total_amount or 0)/100:.2f}")
                    st.divider()
            
        else:
            if total_companies == 0:
                st.info("👋 Welcome! Start by adding your first company in the Companies section.")
            else:
                st.info("No billable items yet. Add some work hours in the Billable Items section.")
                
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
        
        # Fallback to placeholder metrics if there's an error
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Companies", "Error")
        
        with col2:
            st.metric("Unbilled Hours", "Error")
        
        with col3:
            st.metric("Unbilled Revenue", "Error")
        
        with col4:
            st.metric("Total Revenue", "Error")

def show_companies():
    """Manage companies"""
    st.header("🏢 Companies")
    
    # Add new company section
    with st.expander("➕ Add New Company", expanded=False):
        with st.form("add_company"):
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Company Name*", placeholder="Acme Corp")
                email = st.text_input("Email", placeholder="billing@acme.com")
                phone = st.text_input("Phone", placeholder="+1 555-123-4567")
                contact_person = st.text_input("Contact Person", placeholder="John Doe")
            
            with col2:
                address = st.text_area("Address", placeholder="123 Business St")
                city = st.text_input("City", placeholder="New York")
                col_state, col_zip = st.columns(2)
                with col_state:
                    state = st.text_input("State", placeholder="NY")
                with col_zip:
                    zip_code = st.text_input("ZIP Code", placeholder="10001")
                country = st.text_input("Country", placeholder="USA")
            
            col_rate, col_currency = st.columns(2)
            with col_rate:
                hourly_rate = st.number_input("Default Hourly Rate ($)", min_value=0.0, step=5.0, value=75.0)
            with col_currency:
                currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD"])
            
            tax_id = st.text_input("Tax ID", placeholder="12-3456789")
            
            if st.form_submit_button("Add Company"):
                if company_name:
                    try:
                        from models.database import SessionLocal
                        from models.company import Company
                        
                        # Create database session
                        db = SessionLocal()
                        
                        # Create new company instance
                        new_company = Company(
                            name=company_name,
                            email=email if email else None,
                            phone=phone if phone else None,
                            contact_person=contact_person if contact_person else None,
                            address=address if address else None,
                            city=city if city else None,
                            state=state if state else None,
                            zip_code=zip_code if zip_code else None,
                            country=country if country else None,
                            default_hourly_rate=int(hourly_rate * 100) if hourly_rate > 0 else None,  # Store in cents
                            currency=currency,
                            tax_id=tax_id if tax_id else None
                        )
                        
                        # Add to database
                        db.add(new_company)
                        db.commit()
                        db.close()
                        
                        st.success(f"Company '{company_name}' added successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error adding company: {str(e)}")
                else:
                    st.error("Company name is required!")
    
    # List existing companies
    st.subheader("Existing Companies")
    
    try:
        from models.database import SessionLocal
        from models.company import Company
        
        # Get companies from database
        db = SessionLocal()
        companies = db.query(Company).filter(Company.is_active == True).all()
        db.close()
        
        if companies:
            for company in companies:
                with st.expander(f"🏢 {company.name}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Contact:** {company.contact_person or 'Not specified'}")
                        st.write(f"**Email:** {company.email or 'Not specified'}")
                        st.write(f"**Phone:** {company.phone or 'Not specified'}")
                        st.write(f"**Tax ID:** {company.tax_id or 'Not specified'}")
                    
                    with col2:
                        st.write(f"**Address:** {company.formatted_address or 'Not specified'}")
                        st.write(f"**Default Rate:** ${company.default_hourly_rate/100:.2f}/hour" if company.default_hourly_rate else "Not specified")
                        st.write(f"**Currency:** {company.currency}")
                        st.write(f"**Created:** {company.created_at.strftime('%Y-%m-%d') if company.created_at else 'Unknown'}")
                    
                    # Action buttons
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.button(f"Edit {company.name}", key=f"edit_{company.id}"):
                            st.info("Edit functionality coming soon!")
                    with col_delete:
                        if st.button(f"Delete {company.name}", key=f"delete_{company.id}", type="secondary"):
                            st.warning("Delete functionality coming soon!")
        else:
            st.info("No companies found. Add your first company above.")
            
    except Exception as e:
        st.error(f"Error loading companies: {str(e)}")

def show_billable_items():
    """Manage billable items"""
    st.header("⏰ Billable Items")
    
    # Add manual billable item
    with st.expander("➕ Add Billable Item", expanded=False):
        with st.form("add_billable_item"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Load companies from database
                try:
                    from models.database import SessionLocal
                    from models.company import Company
                    
                    db = SessionLocal()
                    companies = db.query(Company).filter(Company.is_active == True).all()
                    db.close()
                    
                    if companies:
                        company_options = {f"{comp.name}": comp.id for comp in companies}
                        selected_company_name = st.selectbox("Company*", list(company_options.keys()))
                        selected_company_id = company_options.get(selected_company_name)
                    else:
                        st.selectbox("Company*", ["No companies available"])
                        selected_company_id = None
                        st.warning("Please add a company first before adding billable items.")
                        
                except Exception as e:
                    st.selectbox("Company*", ["Error loading companies"])
                    selected_company_id = None
                    st.error(f"Error loading companies: {str(e)}")
                description = st.text_area("Description*", placeholder="Development work on project X")
                project = st.text_input("Project", placeholder="Project Alpha")
            
            with col2:
                date_worked = st.date_input("Date Worked*", value=datetime.now().date())
                hours = st.number_input("Hours*", min_value=0.0, step=0.25, value=1.0)
                hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, step=5.0, help="Leave empty to use company default")
                task_category = st.text_input("Task Category", placeholder="Development")
            
            if st.form_submit_button("Add Billable Item"):
                if description and hours > 0 and selected_company_id:
                    try:
                        from models.database import SessionLocal
                        from models.billable_item import BillableItem
                        from datetime import datetime as dt
                        
                        # Create database session
                        db = SessionLocal()
                        
                        # Create new billable item instance
                        new_item = BillableItem(
                            company_id=selected_company_id,
                            description=description,
                            project=project if project else None,
                            task_category=task_category if task_category else None,
                            date_worked=dt.combine(date_worked, dt.min.time()),  # Convert date to datetime
                            hours=hours,
                            hourly_rate=int(hourly_rate * 100) if hourly_rate > 0 else None,  # Store in cents
                        )
                        
                        # Add to database first
                        db.add(new_item)
                        db.flush()  # Ensure the item is saved but transaction not committed
                        
                        # Calculate and store total amount (requires the company relationship)
                        new_item.update_total_amount()
                        
                        # Commit the transaction
                        db.commit()
                        db.close()
                        
                        st.success("Billable item added successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error adding billable item: {str(e)}")
                elif not selected_company_id:
                    st.error("Please select a company!")
                else:
                    st.error("Description and hours are required!")
    
    # Display billable items
    st.subheader("Recent Billable Items")
    
    try:
        from models.database import SessionLocal
        from models.billable_item import BillableItem
        from models.company import Company
        
        # Get billable items from database with eager loading
        from sqlalchemy.orm import joinedload
        
        db = SessionLocal()
        billable_items = db.query(BillableItem).options(joinedload(BillableItem.company)).filter(
            BillableItem.is_invoiced == False
        ).order_by(BillableItem.date_worked.desc()).limit(20).all()
        db.close()
        
        if billable_items:
            # Calculate amounts while session is active
            for item in billable_items:
                if not item.total_amount:
                    item.update_total_amount()
            
            # Summary stats
            total_hours = sum(float(item.hours) for item in billable_items)
            total_amount = sum(item.total_amount or 0 for item in billable_items) / 100  # Convert from cents
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Unbilled Hours", f"{total_hours:.2f}")
            with col2:
                st.metric("Unbilled Amount", f"${total_amount:.2f}")
            with col3:
                st.metric("Total Items", len(billable_items))
            
            st.markdown("---")
            
            # Display items in a table format
            items_data = []
            for item in billable_items:
                items_data.append({
                    "Date": item.date_worked.strftime("%Y-%m-%d"),
                    "Company": item.company.name,
                    "Project": item.project or "—",
                    "Description": item.description[:50] + "..." if len(item.description) > 50 else item.description,
                    "Category": item.task_category or "—",
                    "Hours": float(item.hours),
                    "Rate": f"${item.hourly_rate/100:.2f}" if item.hourly_rate else f"${item.company.default_hourly_rate/100:.2f}" if item.company.default_hourly_rate else "—",
                    "Amount": f"${(item.total_amount or 0)/100:.2f}"
                })
            
            # Create DataFrame and display
            df = pd.DataFrame(items_data)
            st.dataframe(df, use_container_width=True)
            
            # Expandable details for each item
            st.subheader("Item Details")
            for item in billable_items[:10]:  # Show first 10 items
                with st.expander(f"📋 {item.company.name} - {item.date_worked.strftime('%Y-%m-%d')} ({item.hours}h)", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Company:** {item.company.name}")
                        st.write(f"**Date:** {item.date_worked.strftime('%Y-%m-%d')}")
                        st.write(f"**Hours:** {item.hours}")
                        st.write(f"**Project:** {item.project or 'Not specified'}")
                        st.write(f"**Category:** {item.task_category or 'Not specified'}")
                    
                    with col2:
                        st.write(f"**Rate:** ${item.hourly_rate/100:.2f}/hour" if item.hourly_rate else f"${item.company.default_hourly_rate/100:.2f}/hour (default)" if item.company.default_hourly_rate else "No rate set")
                        st.write(f"**Total:** ${(item.total_amount or 0)/100:.2f}")
                        st.write(f"**Status:** {'Invoiced' if item.is_invoiced else 'Unbilled'}")
                        st.write(f"**Created:** {item.created_at.strftime('%Y-%m-%d %H:%M') if item.created_at else 'Unknown'}")
                    
                    st.write(f"**Description:** {item.description}")
                    
                    # Action buttons
                    col_edit, col_delete, col_invoice = st.columns(3)
                    with col_edit:
                        if st.button(f"Edit", key=f"edit_item_{item.id}"):
                            st.info("Edit functionality coming soon!")
                    with col_delete:
                        if st.button(f"Delete", key=f"delete_item_{item.id}", type="secondary"):
                            st.warning("Delete functionality coming soon!")
                    with col_invoice:
                        if not item.is_invoiced:
                            if st.button(f"Mark Invoiced", key=f"invoice_item_{item.id}"):
                                st.info("Invoice functionality coming soon!")
        else:
            st.info("No billable items found. Add items manually or import from a file.")
            
    except Exception as e:
        st.error(f"Error loading billable items: {str(e)}")

def show_import_data():
    """Import data from files"""
    st.header("📁 Import Data")
    
    # File upload section
    st.subheader("Upload File")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a file containing billable hours data"
    )
    
    if uploaded_file is not None:
        # Save uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / uploaded_file.name
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        
        # Preview file contents
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(file_path).head(10)
            else:
                df = pd.read_excel(file_path).head(10)
            
            st.subheader("File Preview")
            st.dataframe(df)
            
            # Column mapping section
            st.subheader("Column Mapping")
            st.info("Map your file columns to the required fields:")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                description_col = st.selectbox("Description Column*", options=list(df.columns))
            with col2:
                date_col = st.selectbox("Date Column*", options=list(df.columns))
            with col3:
                hours_col = st.selectbox("Hours Column*", options=list(df.columns))
            
            col4, col5, col6 = st.columns(3)
            with col4:
                project_col = st.selectbox("Project Column (Optional)", options=["None"] + list(df.columns))
            with col5:
                category_col = st.selectbox("Category Column (Optional)", options=["None"] + list(df.columns))
            with col6:
                rate_col = st.selectbox("Hourly Rate Column (Optional)", options=["None"] + list(df.columns))
            
            # Company selection
            try:
                from models.database import SessionLocal
                from models.company import Company
                
                db = SessionLocal()
                companies = db.query(Company).filter(Company.is_active == True).all()
                db.close()
                
                if companies:
                    company_options = {f"{comp.name}": comp.id for comp in companies}
                    selected_company_name = st.selectbox("Select Company*", list(company_options.keys()))
                    selected_company_id = company_options.get(selected_company_name)
                else:
                    st.selectbox("Select Company*", ["No companies available"])
                    selected_company_id = None
                    st.warning("Please add a company first before importing data.")
                    
            except Exception as e:
                st.selectbox("Select Company*", ["Error loading companies"])
                selected_company_id = None
                st.error(f"Error loading companies: {str(e)}")
            
            if st.button("Import Data", type="primary"):
                st.warning("Import functionality will be implemented after companies are set up.")
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

def show_generate_invoice():
    """Generate invoices"""
    st.header("📄 Generate Invoice")
    
    # Import Path for file operations
    from pathlib import Path
    
    # Show existing invoices
    try:
        from models.database import SessionLocal
        from models.invoice import Invoice
        from models.company import Company
        from sqlalchemy.orm import joinedload
        from pathlib import Path
        
        db = SessionLocal()
        recent_invoices = db.query(Invoice).options(joinedload(Invoice.company)).order_by(Invoice.created_at.desc()).limit(5).all()
        
        if recent_invoices:
            st.subheader("📋 Recent Invoices")
            
            for invoice in recent_invoices:
                with st.expander(f"📄 {invoice.invoice_number} - {invoice.company.name} - {invoice.formatted_total}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Status:** {invoice.status.value.title()}")
                        st.write(f"**Date:** {invoice.invoice_date.strftime('%Y-%m-%d')}")
                        st.write(f"**Due Date:** {invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else 'N/A'}")
                        st.write(f"**Company:** {invoice.company.name}")
                    
                    with col2:
                        st.write(f"**Subtotal:** ${invoice.subtotal/100:.2f}")
                        if invoice.tax_amount > 0:
                            st.write(f"**Tax:** ${invoice.tax_amount/100:.2f}")
                        st.write(f"**Total:** {invoice.formatted_total}")
                        st.write(f"**Created:** {invoice.created_at.strftime('%Y-%m-%d %H:%M') if invoice.created_at else 'Unknown'}")
                    
                    if invoice.notes:
                        st.write(f"**Notes:** {invoice.notes}")
                    
                    # Download button if PDF exists
                    if invoice.pdf_path and Path(invoice.pdf_path).exists():
                        with open(invoice.pdf_path, "rb") as pdf_file:
                            st.download_button(
                                label="📄 Download PDF",
                                data=pdf_file.read(),
                                file_name=f"invoice_{invoice.invoice_number.replace('/', '_')}.pdf",
                                mime="application/pdf",
                                key=f"download_invoice_{invoice.id}"
                            )
        
        db.close()
        
    except Exception as e:
        st.error(f"Error loading recent invoices: {str(e)}")
    
    st.markdown("---")
    
    # Preview section - show unbilled items by company
    st.subheader("💼 Preview Unbilled Items")
    
    try:
        from models.billable_item import BillableItem
        
        db = SessionLocal()
        
        # Get companies with unbilled items
        companies_with_items = db.query(Company).join(BillableItem).filter(
            BillableItem.is_invoiced == False,
            Company.is_active == True
        ).distinct().all()
        
        if companies_with_items:
            # Show summary for each company
            for company in companies_with_items:
                unbilled_items = db.query(BillableItem).filter(
                    BillableItem.company_id == company.id,
                    BillableItem.is_invoiced == False
                ).all()
                
                # Calculate amounts while session is active
                for item in unbilled_items:
                    if not item.total_amount:
                        item.update_total_amount()
                
                total_hours = sum(float(item.hours) for item in unbilled_items)
                total_amount = sum(item.total_amount or 0 for item in unbilled_items) / 100
                
                with st.expander(f"🏢 {company.name} - {len(unbilled_items)} items - {total_hours:.1f}h - ${total_amount:.2f}", expanded=False):
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Items", len(unbilled_items))
                    with col2:
                        st.metric("Hours", f"{total_hours:.1f}")
                    with col3:
                        st.metric("Amount", f"${total_amount:.2f}")
                    
                    # Item details
                    st.write("**Items to be invoiced:**")
                    for item in unbilled_items:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"• {item.description[:50]}{'...' if len(item.description) > 50 else ''}")
                        with col2:
                            st.write(f"{item.hours}h")
                        with col3:
                            st.write(f"${(item.total_amount or 0)/100:.2f}")
        else:
            st.info("No unbilled items found. Add some billable items first!")
        
        db.close()
        
    except Exception as e:
        st.error(f"Error loading preview: {str(e)}")
    
    st.markdown("---")
    
    # Invoice number generation (outside form)
    st.subheader("🔧 Create New Invoice")
    
    col_inv_num, col_refresh = st.columns([3, 1])
    with col_inv_num:
        # Use session state to store the invoice number
        if 'invoice_number' not in st.session_state:
            st.session_state.invoice_number = generate_unique_invoice_number()
        
        invoice_number_display = st.text_input("Invoice Number*", value=st.session_state.invoice_number, key="invoice_number_input")
    
    with col_refresh:
        st.write("")  # Empty space for alignment
        if st.button("🔄 New Number", help="Generate a new unique invoice number"):
            st.session_state.invoice_number = generate_unique_invoice_number()
            st.rerun()
    
    # Invoice generation form
    with st.form("generate_invoice"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Invoice Details")
            # Load companies from database
            try:
                from models.database import SessionLocal
                from models.company import Company
                
                db = SessionLocal()
                companies = db.query(Company).filter(Company.is_active == True).all()
                db.close()
                
                if companies:
                    company_options = {f"{comp.name}": comp.id for comp in companies}
                    selected_company_name = st.selectbox("Company*", list(company_options.keys()))
                    selected_company_id = company_options.get(selected_company_name)
                else:
                    st.selectbox("Company*", ["No companies available"])
                    selected_company_id = None
                    st.warning("Please add a company first before generating invoices.")
                    
            except Exception as e:
                st.selectbox("Company*", ["Error loading companies"])
                selected_company_id = None
                st.error(f"Error loading companies: {str(e)}")
            # Use the invoice number from outside the form
            invoice_number = invoice_number_display
            
            invoice_date = st.date_input("Invoice Date", value=datetime.now().date())
            due_date = st.date_input("Due Date", value=(datetime.now() + timedelta(days=30)).date())
        
        with col2:
            st.subheader("Settings")
            tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, step=0.25, value=23.0)
            currency = st.selectbox("Currency", ["PLN", "USD", "EUR", "GBP", "CAD"])
            format_type = st.selectbox("Output Format", ["PDF", "Word Document", "Both"])
            invoice_language = st.selectbox("Invoice Language", ["Polish (Faktura)", "English (Invoice)"])
            
            # Show header status for Polish invoices
            if invoice_language == "Polish (Faktura)":
                header_path = Path("assets/invoice_header.png")
                if header_path.exists():
                    st.success("🎨 Custom header will be used as background")
                else:
                    st.info("ℹ️ Using default text header (upload header in Settings for custom background)")
        
        notes = st.text_area("Notes", placeholder="Additional notes for the invoice...")
        terms = st.text_area("Terms", placeholder="Payment terms and conditions...")
        
        if st.form_submit_button("Generate Invoice", type="primary"):
            if selected_company_id and invoice_number:
                try:
                    from models.database import SessionLocal
                    from models.invoice import Invoice, InvoiceStatus
                    from models.invoice_item import InvoiceItem
                    from models.billable_item import BillableItem
                    from models.company import Company
                    from services.pdf_generator import InvoicePDFGenerator
                    from sqlalchemy.orm import joinedload
                    from datetime import datetime as dt
                    from pathlib import Path
                    
                    # Create database session
                    db = SessionLocal()
                    
                    # Get company and unbilled items
                    company = db.query(Company).filter(Company.id == selected_company_id).first()
                    unbilled_items = db.query(BillableItem).options(joinedload(BillableItem.company)).filter(
                        BillableItem.company_id == selected_company_id,
                        BillableItem.is_invoiced == False
                    ).all()
                    
                    if not unbilled_items:
                        st.error("No unbilled items found for this company!")
                        db.close()
                        return
                    
                    # Create invoice
                    new_invoice = Invoice(
                        company_id=selected_company_id,
                        invoice_number=invoice_number,
                        invoice_date=dt.combine(invoice_date, dt.min.time()),
                        due_date=dt.combine(due_date, dt.min.time()) if due_date else None,
                        status=InvoiceStatus.DRAFT,
                        tax_rate=int(tax_rate * 100) if tax_rate > 0 else 0,  # Convert to basis points
                        notes=notes if notes else None,
                        terms=terms if terms else None
                    )
                    
                    db.add(new_invoice)
                    db.flush()  # Get the invoice ID
                    
                    # Create invoice items from billable items
                    for item in unbilled_items:
                        # Calculate the unit price while session is active
                        unit_price = item.hourly_rate or (item.company.default_hourly_rate if item.company.default_hourly_rate else 0)
                        
                        # Calculate and store the total amount manually (avoid update_total_amount method)
                        if not item.total_amount:
                            item.total_amount = int(float(item.hours) * unit_price)
                        
                        invoice_item = InvoiceItem(
                            invoice_id=new_invoice.id,
                            description=item.description,
                            quantity=float(item.hours),
                            unit_price=unit_price,
                            project=item.project,
                            task_category=item.task_category
                        )
                        invoice_item.calculate_total()
                        db.add(invoice_item)
                        
                        # Mark billable item as invoiced
                        item.is_invoiced = True
                        item.invoice_id = new_invoice.id
                    
                    db.flush()  # Ensure invoice items are saved
                    
                    # Calculate invoice totals
                    new_invoice.calculate_totals()
                    
                    # Generate PDF if requested
                    pdf_path = None
                    if format_type in ["PDF", "Both"]:
                        output_dir = Path("invoices")
                        output_dir.mkdir(exist_ok=True)
                        pdf_filename = f"invoice_{invoice_number.replace('/', '_')}.pdf"
                        pdf_path = output_dir / pdf_filename
                        
                        # Get invoice items for PDF generation
                        invoice_items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == new_invoice.id).all()
                        
                        # Generate PDF based on language selection
                        if invoice_language == "Polish (Faktura)":
                            from services.polish_invoice_generator import PolishInvoicePDFGenerator
                            from config.polish_invoice_config import get_polish_seller_info
                            
                            pdf_generator = PolishInvoicePDFGenerator()
                            seller_info = get_polish_seller_info()
                            
                            pdf_generator.generate_polish_invoice_pdf(new_invoice, company, invoice_items, str(pdf_path), seller_info)
                        else:
                            # Use the standard English invoice generator
                            pdf_generator = InvoicePDFGenerator()
                            pdf_generator.generate_invoice_pdf(new_invoice, company, invoice_items, str(pdf_path))
                        
                        new_invoice.pdf_path = str(pdf_path)
                    
                    # Calculate summary metrics before closing session
                    total_items = len(unbilled_items)
                    total_hours = sum(float(item.hours) for item in unbilled_items)
                    invoice_total = new_invoice.total_amount
                    
                    # Commit all changes
                    db.commit()
                    db.close()
                    
                    # Store success info in session state for display outside form
                    st.session_state.invoice_success = {
                        'invoice_number': invoice_number,
                        'total_items': total_items,
                        'total_hours': total_hours,
                        'invoice_total': invoice_total,
                        'pdf_path': str(pdf_path) if pdf_path and pdf_path.exists() else None
                    }
                    
                    st.rerun()
                    
                except Exception as e:
                    db.rollback()
                    db.close()
                    
                    # Provide specific error messages
                    error_message = str(e)
                    if "UNIQUE constraint failed: invoices.invoice_number" in error_message:
                        st.error(f"❌ Invoice number '{invoice_number}' already exists! Please use a different invoice number.")
                        st.info("💡 Tip: Refresh the page to get a new auto-generated unique invoice number.")
                    elif "No unbilled items found" in error_message:
                        st.error("❌ No unbilled items found for this company! Add some billable items first.")
                    else:
                        st.error(f"❌ Error generating invoice: {error_message}")
                    
                    # Suggest solutions
                    with st.expander("🔧 Troubleshooting", expanded=False):
                        st.write("**Common solutions:**")
                        st.write("• Change the invoice number to something unique")
                        st.write("• Make sure the company has unbilled items")
                        st.write("• Check that all required fields are filled")
                        st.write("• Refresh the page and try again")
                    
            else:
                st.error("Please select a company and enter an invoice number!")
    
    # Display success message and download button outside the form
    if 'invoice_success' in st.session_state:
        success_info = st.session_state.invoice_success
        
        # Show success message
        st.success(f"✅ Invoice {success_info['invoice_number']} generated successfully!")
        
        # Show invoice summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Items Invoiced", success_info['total_items'])
        with col2:
            st.metric("Total Hours", f"{success_info['total_hours']:.2f}")
        with col3:
            st.metric("Invoice Total", f"${success_info['invoice_total']/100:.2f}")
        
        # Provide download link if PDF was generated
        if success_info['pdf_path'] and Path(success_info['pdf_path']).exists():
            with open(success_info['pdf_path'], "rb") as pdf_file:
                st.download_button(
                    label="📄 Download Invoice PDF",
                    data=pdf_file.read(),
                    file_name=f"invoice_{success_info['invoice_number'].replace('/', '_')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
        
        # Clear the success state after displaying (optional - you can keep it for persistence)
        # del st.session_state.invoice_success

def show_settings():
    """Application settings"""
    st.header("⚙️ Settings")
    
    # Invoice settings
    st.subheader("Invoice Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Your Company Name", placeholder="Your Business Name")
        st.text_input("Your Email", placeholder="your@email.com")
        st.text_area("Your Address", placeholder="Your business address...")
    
    with col2:
        st.text_input("Your Phone", placeholder="+1 555-123-4567")
        st.text_input("Your Tax ID", placeholder="12-3456789")
        st.text_input("Your Website", placeholder="https://yourbusiness.com")
    
    # Logo upload
    st.subheader("Header/Logo Settings")
    st.info("Upload an A4-sized header image to use as background on Polish invoices")
    
    # Check if header already exists
    header_path = Path("assets/invoice_header.png")
    if header_path.exists():
        st.success(f"✅ Header image is currently saved and will be used on Polish invoices")
        if st.button("🗑️ Remove Current Header"):
            header_path.unlink()
            st.success("Header removed!")
            st.rerun()
    else:
        st.info("ℹ️ No header image currently saved")
    
    logo_file = st.file_uploader("Upload A4 Header/Logo", type=['png', 'jpg', 'jpeg'])
    
    if logo_file is not None:
        # Save the uploaded header
        assets_dir = Path("assets")
        assets_dir.mkdir(exist_ok=True)
        
        header_path = assets_dir / "invoice_header.png"
        
        # Save the uploaded file
        with open(header_path, "wb") as f:
            f.write(logo_file.getbuffer())
        
        st.success(f"✅ Header saved to {header_path}")
        st.image(logo_file, caption="Header Preview (will be used as background on Polish invoices)", width=400)
        
        # Store in session state for the invoice generator to use
        st.session_state.header_image_path = str(header_path)
    
    # Default settings
    st.subheader("Default Settings")
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Default Currency", ["PLN", "USD", "EUR", "GBP", "CAD"])
        st.number_input("Default Tax Rate (%)", min_value=0.0, max_value=100.0, step=0.25, value=23.0)
    with col2:
        st.number_input("Default Payment Terms (Days)", min_value=1, max_value=365, value=14)
        st.selectbox("Default Invoice Format", ["PDF", "Word Document"])
    
    # Polish Invoice Settings
    st.subheader("Polish Invoice Settings (Faktura)")
    st.info("Configure your company information for Polish invoices. These settings will be used as the seller (Sprzedawca) information.")
    
    # Header/Branding section
    st.subheader("Header & Branding")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Header Title", value="bright", help="Główny tytuł w nagłówku")
        st.text_input("Header Subtitle", value="ways to grow", help="Podtytuł w nagłówku")
    with col2:
        st.text_input("Header Description", value="coaching, szkolenia, doradztwo HR", help="Opis działalności")
    
    # Company Information
    st.subheader("Company Information")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Polish Company Name", value="MAGDALENA KOŁODKIEWICZ BRIGHT", help="Nazwa firmy")
        st.text_input("Business Type", value="COACHING SZKOLENIA DORADZTWO HR", help="Rodzaj działalności")
        st.text_input("Address", value="ul. Obrzetska 1a/118", help="Adres")
        st.text_input("City", value="02-691 Warszawa", help="Miasto")
    
    with col2:
        st.text_input("NIP", value="7281339661", help="Numer Identyfikacji Podatkowej")
        st.text_input("REGON", value="", help="Numer REGON (opcjonalny)")
        st.text_input("Phone", value="", help="Telefon (opcjonalny)")
        st.text_input("Email", value="", help="Email (opcjonalny)")
    
    # Bank information for Polish invoices
    st.subheader("Bank Information (for Polish invoices)")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Bank Account Number", value="64 1140 2004 0000 3202 3382 6537", help="Numer konta bankowego")
    with col2:
        st.text_input("Bank Name", value="BRE BANK SA", help="Nazwa banku")
    
    # VAT Settings
    st.subheader("VAT Settings")
    st.number_input("Polish VAT Rate (%)", min_value=0.0, max_value=100.0, step=0.25, value=23.0, help="Standardowa stawka VAT w Polsce")
    
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")
        st.info("Note: To permanently save these settings, you would need to set environment variables or modify the configuration file.")

if __name__ == "__main__":
    main() 