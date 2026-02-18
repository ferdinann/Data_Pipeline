import pytest
import pandas as pd
import os
import logging
from unittest import mock
from utils.load import save_to_csv, save_to_gsheet_api, save_to_postgresql

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'title': ['Product A', 'Product B'],
        'price_idr': [150000.0, 250000.0],
        'rating': [4.5, 3.8],
        'colors': [2, 3],
        'sizes': ['S,M', 'L,XL'],
        'gender': ['men', 'women'],
        'timestamp': ['2025-05-03T00:00:00', '2025-05-03T00:00:00']
    })

def test_save_csv_success(tmp_path, sample_df, caplog):
    caplog.set_level(logging.INFO)

    test_path = tmp_path / "output.csv"
    result = save_to_csv(sample_df, str(test_path))

    assert result is True
    assert os.path.exists(test_path)

    df_read = pd.read_csv(test_path)
    assert len(df_read) == 2
    assert list(df_read.columns) == list(sample_df.columns)

    assert f"Data successfully saved to {test_path}" in caplog.text


def test_save_csv_path_creation(tmp_path, sample_df):
    nested_path = tmp_path / "nested/dirs/output.csv"
    
    result = save_to_csv(sample_df, str(nested_path))
    
    assert result is True
    assert os.path.exists(nested_path)

def test_save_csv_permission_error(tmp_path, sample_df, caplog):
    test_path = tmp_path / "output.csv"
    
    with mock.patch('pandas.DataFrame.to_csv') as mock_save:
        mock_save.side_effect = PermissionError("Write protected")
        result = save_to_csv(sample_df, str(test_path))
    
    assert result is False
    assert "Permission denied: Write protected" in caplog.text

def test_save_csv_invalid_data(tmp_path, caplog):
    empty_df = pd.DataFrame()
    target_path = tmp_path / "empty.csv"

    result = save_to_csv(empty_df, target_path)

    assert result is False
    assert "No data to save" in caplog.text
    assert not target_path.exists()


def test_save_csv_disk_full(tmp_path, sample_df, caplog):
    test_path = tmp_path / "large.csv"
    
    with mock.patch('pandas.DataFrame.to_csv') as mock_save:
        mock_save.side_effect = OSError(28, "No space left on device")
        result = save_to_csv(sample_df, str(test_path))
    
    assert result is False
    assert "Failed to save data: [Errno 28] No space left on device" in caplog.text

def test_save_csv_invalid_path(sample_df, caplog):
    caplog.set_level(logging.INFO)
    result = save_to_csv(sample_df, "/invalid/path/?.csv")
    assert result is False
    assert "OSError while saving: [Errno 22] Invalid argument" in caplog.text


def test_save_to_gsheet_api_success(sample_df, caplog):
    with mock.patch("utils.load.Credentials.from_service_account_file") as mock_creds, \
         mock.patch("utils.load.build") as mock_build:
        
        mock_service = mock.Mock()
        mock_sheet = mock.Mock()
        mock_sheet.values().update().execute.return_value = {}
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        caplog.set_level(logging.INFO)

        result = save_to_gsheet_api(sample_df, "spreadsheet_id", "Sheet1!A1", "dummy_key.json")

        assert result is True
        assert "Data successfully uploaded to Google Sheets" in caplog.text

def test_save_to_gsheet_api_empty(caplog):
    empty_df = pd.DataFrame()
    result = save_to_gsheet_api(empty_df, "spreadsheet_id", "Sheet1!A1", "dummy_key.json")
    assert result is False
    assert "No data to upload to Google Sheets" in caplog.text

def test_save_to_gsheet_api_failure(sample_df, caplog):
    with mock.patch("utils.load.Credentials.from_service_account_file", side_effect=Exception("API error")):
        result = save_to_gsheet_api(sample_df, "spreadsheet_id", "Sheet1!A1", "dummy_key.json")
    assert result is False
    assert "Failed to upload to Google Sheets: API error" in caplog.text

# -------------------------------
# save_to_postgresql tests
# -------------------------------

def test_save_to_postgresql_success(sample_df, caplog):
    caplog.set_level(logging.INFO)

    with mock.patch("utils.load.create_engine") as mock_engine:
        mock_conn = mock.Mock()
        mock_engine.return_value = mock_conn
        with mock.patch.object(sample_df, "to_sql") as mock_to_sql:
            result = save_to_postgresql(sample_df, "postgresql://test", "test_table")

    assert result is True
    assert "Data successfully saved to PostgreSQL table test_table" in caplog.text


def test_save_to_postgresql_empty(caplog):
    empty_df = pd.DataFrame()
    result = save_to_postgresql(empty_df, "postgresql://test", "test_table")
    assert result is False
    assert "No data to save to PostgreSQL" in caplog.text

def test_save_to_postgresql_sqlalchemy_error(sample_df, caplog):
    with mock.patch("utils.load.create_engine") as mock_engine:
        mock_conn = mock.Mock()
        mock_engine.return_value = mock_conn
        with mock.patch.object(sample_df, "to_sql", side_effect=Exception("SQL error")):
            result = save_to_postgresql(sample_df, "postgresql://test", "test_table")
    assert result is False
    assert "Unexpected error while saving to PostgreSQL: SQL error" in caplog.text