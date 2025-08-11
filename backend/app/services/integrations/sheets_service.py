from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.oauth_manager import OAuthManager
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


class SheetsService:
    """Google Sheets integration service for reading and updating spreadsheets"""
    
    def __init__(self, db: Session):
        self.db = db
        self.oauth_manager = OAuthManager(db)
    
    def read_sheet(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Read data from Google Sheets"""
        integration_id = config.get("integration_id")
        if not integration_id:
            raise ValueError("Integration ID not configured")
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        spreadsheet_id = config.get("spreadsheet_id")
        range_name = config.get("range_name", "A1:Z1000")
        
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID not configured")
        
        try:
            # Build Sheets service
            credentials = Credentials(
                token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=token.integration.config.get("client_id"),
                client_secret=token.integration.config.get("client_secret")
            )
            
            service = build('sheets', 'v4', credentials=credentials)
            
            # Read data
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # Convert to structured data if headers are present
            structured_data = []
            if values and config.get("has_headers", True):
                headers = values[0]
                for row in values[1:]:
                    row_data = {}
                    for i, value in enumerate(row):
                        if i < len(headers):
                            row_data[headers[i]] = value
                    structured_data.append(row_data)
            else:
                structured_data = values
            
            return {
                "data": structured_data,
                "raw_values": values,
                "spreadsheet_id": spreadsheet_id,
                "range": range_name,
                "row_count": len(values)
            }
            
        except Exception as e:
            raise Exception(f"Failed to read Google Sheets: {str(e)}")
    
    def update_sheet(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update Google Sheets with data"""
        integration_id = config.get("integration_id")
        if not integration_id:
            raise ValueError("Integration ID not configured")
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        spreadsheet_id = config.get("spreadsheet_id")
        range_name = config.get("range_name", "A1")
        
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID not configured")
        
        # Get data to write
        data_to_write = config.get("data") or input_data.get("data")
        if not data_to_write:
            raise ValueError("No data provided for update")
        
        try:
            # Build Sheets service
            credentials = Credentials(
                token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=token.integration.config.get("client_id"),
                client_secret=token.integration.config.get("client_secret")
            )
            
            service = build('sheets', 'v4', credentials=credentials)
            
            # Prepare data for writing
            if isinstance(data_to_write, list) and data_to_write and isinstance(data_to_write[0], dict):
                # Convert list of dicts to 2D array
                headers = list(data_to_write[0].keys())
                values = [headers]
                for row in data_to_write:
                    values.append([row.get(header, "") for header in headers])
            elif isinstance(data_to_write, list):
                values = data_to_write
            else:
                values = [[data_to_write]]
            
            # Update sheet
            body = {
                'values': values
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return {
                "updated_range": result.get('updatedRange'),
                "updated_rows": result.get('updatedRows'),
                "updated_columns": result.get('updatedColumns'),
                "updated_cells": result.get('updatedCells'),
                "spreadsheet_id": spreadsheet_id
            }
            
        except Exception as e:
            raise Exception(f"Failed to update Google Sheets: {str(e)}")
    
    def append_to_sheet(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Append data to Google Sheets"""
        integration_id = config.get("integration_id")
        if not integration_id:
            raise ValueError("Integration ID not configured")
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        spreadsheet_id = config.get("spreadsheet_id")
        range_name = config.get("range_name", "A:A")
        
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID not configured")
        
        # Get data to append
        data_to_append = config.get("data") or input_data.get("data")
        if not data_to_append:
            raise ValueError("No data provided for append")
        
        try:
            # Build Sheets service
            credentials = Credentials(
                token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=token.integration.config.get("client_id"),
                client_secret=token.integration.config.get("client_secret")
            )
            
            service = build('sheets', 'v4', credentials=credentials)
            
            # Prepare data for appending
            if isinstance(data_to_append, list) and data_to_append and isinstance(data_to_append[0], dict):
                # Convert list of dicts to 2D array
                headers = list(data_to_append[0].keys())
                values = []
                for row in data_to_append:
                    values.append([row.get(header, "") for header in headers])
            elif isinstance(data_to_append, list):
                values = data_to_append
            else:
                values = [[data_to_append]]
            
            # Append to sheet
            body = {
                'values': values
            }
            
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return {
                "updated_range": result.get('updates', {}).get('updatedRange'),
                "updated_rows": result.get('updates', {}).get('updatedRows'),
                "updated_columns": result.get('updates', {}).get('updatedColumns'),
                "updated_cells": result.get('updates', {}).get('updatedCells'),
                "spreadsheet_id": spreadsheet_id
            }
            
        except Exception as e:
            raise Exception(f"Failed to append to Google Sheets: {str(e)}")
    
    def get_spreadsheet_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a Google Sheets spreadsheet"""
        integration_id = config.get("integration_id")
        if not integration_id:
            raise ValueError("Integration ID not configured")
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        spreadsheet_id = config.get("spreadsheet_id")
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID not configured")
        
        try:
            # Build Sheets service
            credentials = Credentials(
                token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=token.integration.config.get("client_id"),
                client_secret=token.integration.config.get("client_secret")
            )
            
            service = build('sheets', 'v4', credentials=credentials)
            
            # Get spreadsheet metadata
            result = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets_info = []
            for sheet in result.get('sheets', []):
                sheet_props = sheet.get('properties', {})
                sheets_info.append({
                    "sheet_id": sheet_props.get('sheetId'),
                    "title": sheet_props.get('title'),
                    "index": sheet_props.get('index'),
                    "grid_properties": sheet_props.get('gridProperties', {})
                })
            
            return {
                "spreadsheet_id": spreadsheet_id,
                "title": result.get('properties', {}).get('title'),
                "sheets": sheets_info,
                "sheets_count": len(sheets_info)
            }
            
        except Exception as e:
            raise Exception(f"Failed to get spreadsheet info: {str(e)}")
    
    def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Google Sheets connection"""
        integration_id = config.get("integration_id")
        if not integration_id:
            return {"status": "error", "message": "Integration ID not configured"}
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            return {"status": "error", "message": "No valid OAuth token found"}
        
        try:
            credentials = Credentials(
                token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=token.integration.config.get("client_id"),
                client_secret=token.integration.config.get("client_secret")
            )
            
            service = build('sheets', 'v4', credentials=credentials)
            
            # Test by getting user's spreadsheets
            result = service.spreadsheets().get(
                spreadsheetId="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"  # Sample spreadsheet
            ).execute()
            
            return {
                "status": "success",
                "title": result.get('properties', {}).get('title'),
                "sheets_count": len(result.get('sheets', []))
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)} 