import os
import json
import logging
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_google_sheets_service():
    """Create and return a Google Sheets API service."""
    try:
        # Get credentials from environment variable
        credentials_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
        
        if not credentials_json:
            logger.error("Google Sheets credentials not found in environment variables")
            return None
        
        try:
            # Try to parse the JSON credentials
            credentials_info = json.loads(credentials_json)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON credentials format: {str(e)}")
            return None
        
        # Create credentials object
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Build the service
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        logger.error(f"Error creating Google Sheets service: {str(e)}")
        return None

def initialize_spreadsheet():
    """Initialize the spreadsheet with headers if it doesn't exist."""
    try:
        service = get_google_sheets_service()
        if not service:
            return False
            
        sheet_id = os.environ.get('GOOGLE_SHEET_ID')
        
        # Set up column headers for the sheet
        headers = [
            "ID", "Date Added", "Head of Household", "Head Phone", 
            "Marital Status", "Spouse Name", "Spouse Phone", 
            "Address", "Children Count", "Child Names", "Child DOBs", "Child Ages", "Child Marital Statuses"
        ]
        
        # Check if headers already exist
        range_name = 'Sheet1!A1:M1'
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        # If no headers exist, add them
        if not values:
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            logger.info("Spreadsheet initialized with headers")
        return True
    except Exception as e:
        logger.error(f"Error initializing spreadsheet: {str(e)}")
        return False

def add_family_to_spreadsheet(family):
    """Add a family record to the Google Sheet."""
    try:
        service = get_google_sheets_service()
        if not service:
            return False
            
        sheet_id = os.environ.get('GOOGLE_SHEET_ID')
        
        # Format the date
        date_added = family.created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # Collect child information
        children = family.children or []
        children_count = len(children)
        child_names = ", ".join([child.name for child in children]) if children else "N/A"
        child_dobs = ", ".join([child.date_of_birth.strftime('%Y-%m-%d') for child in children]) if children else "N/A"
        child_ages = ", ".join([str(child.age) for child in children]) if children else "N/A"
        child_marital_statuses = ", ".join([child.marital_status for child in children]) if children else "N/A"
        
        # Create row data
        row_data = [
            str(family.id),
            date_added,
            family.head_name,
            family.head_phone,
            family.marital_status,
            family.spouse_name or "N/A",
            family.spouse_phone or "N/A",
            family.address or "N/A",
            str(children_count),
            child_names,
            child_dobs,
            child_ages,
            child_marital_statuses
        ]
        
        # Find the next available row
        range_name = 'Sheet1!A:A'
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        next_row = len(values) + 1
        
        # Write the data
        range_to_update = f'Sheet1!A{next_row}:M{next_row}'
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_to_update,
            valueInputOption='RAW',
            body={'values': [row_data]}
        ).execute()
        
        logger.info(f"Family ID {family.id} added to spreadsheet")
        return True
    except Exception as e:
        logger.error(f"Error adding family to spreadsheet: {str(e)}")
        return False