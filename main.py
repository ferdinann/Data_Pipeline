import logging
from datetime import datetime
from utils.extract import extract_data
from utils.transform import transform_data
from utils.load import save_to_csv, save_to_postgresql, save_to_gsheet_api


def setup_logging():
    """Mengatur konfigurasi logging untuk seluruh proses ETL"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('etl_pipeline.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def run_etl_pipeline():
    """Fungsi utama yang mengeksekusi seluruh alur ETL dari awal hingga selesai"""
    try:
        # Mencatat waktu mulai proses ETL
        logging.info("[START] Starting ETL Pipeline")
        start_time = datetime.now()

        # Tahap pengambilan data dari sumber
        logging.info("[EXTRACT] Starting Extraction Phase")
        raw_data = extract_data()
        logging.info(f"[EXTRACT] Successfully extracted {len(raw_data)} items")

        # Tahap pengambilan data dari sumber
        logging.info("[TRANSFORM] Starting Transformation Phase")
        transformed_data = transform_data(raw_data)
        logging.info(f"[TRANSFORM] Transformed {len(transformed_data)} records")

        # Penyimpanan ke file CSV
        logging.info("[LOAD] Saving to CSV")
        if save_to_csv(transformed_data, "products.csv"):
            logging.info("[CSV] Data successfully saved to output.csv")
        else:
            logging.error("[CSV] Failed to save data to CSV")

        # Penyimpanan ke database PostgreSQL
        logging.info("[LOAD] Saving to PostgreSQL")
        postgres_url = "postgresql://etl_user:admin123@localhost:5432/etl_db"  
        if save_to_postgresql(transformed_data, db_url=postgres_url, table_name="etl_data"):
            logging.info("[POSTGRESQL] Data successfully saved to PostgreSQL")
        else:
            logging.error("[POSTGRESQL] Failed to save data to PostgreSQL")

        # Penyimpanan ke Google Sheets melalui API
        logging.info("[LOAD] Saving to Google Sheets")
        if save_to_gsheet_api(transformed_data, spreadsheet_id="1jnZOc4bzpWzbL-MSA0aH9r07cZ7akpKXBzAl7M4qvWI", range_name="Sheet1!A1", json_key_path="google-sheets-api.json"):
            logging.info("[GSHEET] Data uploaded to Google Sheets successfully")
        else:
            logging.error("[GSHEET] Failed to upload to Google Sheets")


        duration = datetime.now() - start_time
        logging.info(f"[DONE] ETL Pipeline completed in {duration.total_seconds():.2f} seconds")

    except Exception as e:
        logging.error(f"[CRITICAL] Pipeline failure: {str(e)}", exc_info=True)

if __name__ == "__main__":
    setup_logging()
    run_etl_pipeline()