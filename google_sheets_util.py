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
            "ID", "Date Added", "Head of Household", "Head GAM", 
            "Marital Status", "Spouse Name", "Spouse GAM", 
            "CITY USA", "Children Count",
            "Child 1 Name", "Child 1 DOB", "Child 1 Status",
            "Child 2 Name", "Child 2 DOB", "Child 2 Status",
            "Child 3 Name", "Child 3 DOB", "Child 3 Status",
            "Child 4 Name", "Child 4 DOB", "Child 4 Status",
            "Child 5 Name", "Child 5 DOB", "Child 5 Status"
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
        # Create base row data
        row_data = [
            str(family.id),
            date_added,
            family.head_name,
            family.head_phone,
            family.marital_status,
            family.spouse_name or "N/A",
            family.spouse_phone or "N/A",
            family.address or "CITY USA",
            str(children_count)
        ]
        
        # Add data for each possible child (up to 5)
        for i in range(5):
            if i < len(children):
                child = children[i]
                row_data.extend([
                    child.name,
                    child.date_of_birth.strftime('%d/%m'),
                    child.marital_status
                ])
            else:
                row_data.extend(["N/A", "N/A", "N/A"])
        
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