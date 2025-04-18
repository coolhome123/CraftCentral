import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_credentials():
    """Check and validate the Google Sheets credentials."""
    print("\n=== Google Sheets Credentials Check ===\n")
    
    # Check if credentials are set
    creds = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
    if not creds:
        print("❌ ERROR: GOOGLE_SHEETS_CREDENTIALS not found in environment variables.")
        print("   Please set this variable with your Google service account credentials.")
        return False
    
    # Check if it's a JSON string
    try:
        creds_data = json.loads(creds)
        print("✅ Credentials format: Valid JSON string")
        
        # Check for required fields
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            print(f"❌ ERROR: Missing required fields in credentials: {', '.join(missing_fields)}")
            print("   Please ensure your service account credentials are complete.")
            return False
        else:
            print("✅ Credentials content: All required fields present")
            print(f"   Service account: {creds_data.get('client_email')}")
            print(f"   Project ID: {creds_data.get('project_id')}")
    except json.JSONDecodeError:
        print("❌ ERROR: Credentials are not in valid JSON format.")
        print("   Please check that the GOOGLE_SHEETS_CREDENTIALS is properly formatted JSON.")
        return False
    
    # Check if sheet ID is set
    sheet_id = os.environ.get('GOOGLE_SHEET_ID')
    if not sheet_id:
        print("❌ ERROR: GOOGLE_SHEET_ID not found in environment variables.")
        print("   Please set this variable with your Google Sheet ID.")
        return False
    else:
        print(f"✅ Sheet ID: {sheet_id}")
    
    print("\n✅ Basic credential check passed! However, we cannot fully verify access to the Google Sheet without testing an API call.")
    print("   Please try submitting a form to test the integration, and check the application logs for any errors.")
    print("\nReminder:")
    print("1. Make sure the Google Sheets API is enabled for your project.")
    print("2. Ensure the service account has Editor access to the Google Sheet.")
    print("3. The Google Sheet should exist and be accessible by the service account.")
    
    return True

if __name__ == "__main__":
    check_credentials()