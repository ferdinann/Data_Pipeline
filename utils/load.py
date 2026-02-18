import pandas as pd
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def save_to_csv(df: pd.DataFrame, file_path: str = 'output.csv') -> bool:
    """Menyimpan DataFrame ke file CSV dengan penanganan error dasar"""
    try:
        # Cek apakah DataFrame kosong sebelum menyimpan
        if df.empty:
            logging.error("No data to save")
            return False
        
        # Pastikan direktori tujuan ada
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        df.to_csv(file_path, index=False)
        logging.info(f"Data successfully saved to {file_path}")
        return True

    except PermissionError as e:
        logging.error(f"Permission denied: {str(e)}")
        return False
    except OSError as e:
        if e.errno == 28:
            logging.error(f"Failed to save data: {str(e)}")
        else:
            logging.error(f"OSError while saving: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Invalid path: {str(e)}")
        return False


def save_to_gsheet_api(df: pd.DataFrame, spreadsheet_id: str, range_name: str, json_key_path: str) -> bool:
    """Mengunggah DataFrame ke Google Sheets menggunakan Google Sheets API"""
    try:
        # Pastikan ada data sebelum proses upload
        if df.empty:
            logging.error("No data to upload to Google Sheets")
            return False
        
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(json_key_path, scopes=scope)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        # Konversi kolom timestamp ke string agar kompatibel dengan Sheets
        df_serializable = df.copy()
        df_serializable['timestamp'] = df_serializable['timestamp'].astype(str)
        # Siapkan data dalam format list of lists (header + values)
        values = [df_serializable.columns.tolist()] + df_serializable.values.tolist()

        body = {'values': values}
        # Update range yang ditentukan dengan mode RAW (tanpa parsing formula)
        result = sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        logging.info("Data successfully uploaded to Google Sheets")
        return True
    except Exception as e:
        logging.error(f"Failed to upload to Google Sheets: {str(e)}")
        return False


def save_to_postgresql(df: pd.DataFrame, db_url: str, table_name: str) -> bool:
    """Menyimpan DataFrame ke tabel PostgreSQL menggunakan SQLAlchemy"""
    try:
        if df.empty:
            logging.error("No data to save to PostgreSQL")
            return False
        engine = create_engine(db_url)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info(f"Data successfully saved to PostgreSQL table {table_name}")
        return True
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error while saving to PostgreSQL: {str(e)}")
        return False