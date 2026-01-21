import pandas as pd
from datetime import datetime, date, timedelta
from src.models import Staff

def load_staff_from_excel(file_path):
    df = pd.read_excel(file_path)
    staff_list = []
    
    for _, row in df.iterrows():
        def clean_date_input(val):
            if pd.isna(val) or str(val).strip().upper() in ["N/A", "NONE", ""]:
                return []
            
            # If Excel already made it a datetime/Timestamp, convert to list
            if isinstance(val, (datetime, date, pd.Timestamp)):
                return [val.date() if hasattr(val, 'date') else val]
            
            # If it's a string, split and parse
            date_list = []
            for part in str(val).split(','):
                try:
                    # Remove time if present (e.g., 2026-01-01 00:00:00 -> 2026-01-01)
                    clean_str = str(part).strip().split(' ')[0]
                    date_list.append(datetime.strptime(clean_str, "%Y-%m-%d").date())
                except:
                    continue
            return date_list
        
        def parse_single_date(val):
            """Helper to convert Excel date cell to a Python date object"""
            if pd.isna(val) or str(val).strip() == "":
                return None
            try:
                # Convert pandas timestamp to python date
                return pd.to_datetime(val).date()
            except:
                return None

        staff = Staff(
            name=str(row['Name']),
            role=Role[row['Role'].strip()],
            ytd_points=float(row['Ytd Points']),
            blackout_dates=set(clean_date_input(row.get('Blackout Dates', ""))),
            bidding_dates=set(clean_date_input(row.get('PH Bidding', ""))),
            last_PH=parse_single_date(row.get('Last PH Worked', "")),
        )
        staff_list.append(staff)
        
    return staff_list