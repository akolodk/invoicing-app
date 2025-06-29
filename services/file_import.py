import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from sqlalchemy.orm import Session
from models import BillableItem, Company

logger = logging.getLogger(__name__)

class FileImportService:
    """Service for importing billable hours from CSV and Excel files"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def import_file(self, file_path: str, company_id: int, column_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Import billable hours from a file"""
        try:
            # Determine file type and read data
            file_path = Path(file_path)
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
            # Apply column mapping if provided
            if column_mapping:
                df = df.rename(columns=column_mapping)
            
            # Validate required columns
            required_columns = ['description', 'date_worked', 'hours']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Process and import rows
            imported_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    billable_item = self._create_billable_item(row, company_id, file_path.name)
                    self.db.add(billable_item)
                    imported_count += 1
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
            
            # Commit changes
            self.db.commit()
            
            return {
                'success': True,
                'imported_count': imported_count,
                'total_rows': len(df),
                'errors': errors,
                'file_name': file_path.name
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error importing file {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'imported_count': 0,
                'total_rows': 0,
                'errors': []
            }
    
    def _create_billable_item(self, row: pd.Series, company_id: int, import_source: str) -> BillableItem:
        """Create a BillableItem from a row of data"""
        # Parse date
        try:
            if isinstance(row['date_worked'], str):
                date_worked = pd.to_datetime(row['date_worked']).to_pydatetime()
            else:
                date_worked = row['date_worked']
        except Exception as e:
            raise ValueError(f"Invalid date format: {row['date_worked']}")
        
        # Parse hours
        try:
            hours = float(row['hours'])
            if hours <= 0:
                raise ValueError("Hours must be positive")
        except Exception as e:
            raise ValueError(f"Invalid hours value: {row['hours']}")
        
        # Create billable item
        billable_item = BillableItem(
            company_id=company_id,
            description=str(row['description']),
            project=str(row.get('project', '')) if pd.notna(row.get('project')) else None,
            task_category=str(row.get('task_category', '')) if pd.notna(row.get('task_category')) else None,
            date_worked=date_worked,
            hours=hours,
            hourly_rate=self._parse_rate(row.get('hourly_rate')),
            import_source=import_source,
            import_date=datetime.now()
        )
        
        # Calculate total amount
        billable_item.update_total_amount()
        
        return billable_item
    
    def _parse_rate(self, rate_value) -> Optional[int]:
        """Parse hourly rate value to cents"""
        if pd.isna(rate_value) or rate_value == '':
            return None
        
        try:
            rate_str = str(rate_value).replace('$', '').replace(',', '')
            rate_float = float(rate_str)
            return int(rate_float * 100)  # Convert to cents
        except:
            return None 