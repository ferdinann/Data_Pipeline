import pytest
import requests_mock
import requests
from utils.extract import extract_data
import logging
from utils import extract

@pytest.fixture
def mock_product_html():
    return """
    <div class="collection-card">
        <div style="position: relative;">
            <img src="https://picsum.photos/280/350?random=2" class="collection-image" alt="T-shirt 2">
            
        </div>
        <div class="product-details">
            <h3 class="product-title">T-shirt 2</h3>
            <div class="price-container"><span class="price">$102.15</span></div>
            <p style="font-size: 14px; color: #777;">Rating: ⭐ 3.9 / 5</p>
            <p style="font-size: 14px; color: #777;">3 Colors</p>
            <p style="font-size: 14px; color: #777;">Size: M</p>
            <p style="font-size: 14px; color: #777;">Gender: Women</p>
        </div>
    </div>
    """

@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m

def test_scrape_products_success(mock_requests, mock_product_html):
    mock_requests.get(
        "https://fashion-studio.dicoding.dev/",
        text=f"<html><body>{mock_product_html * 3}</body></html>"
    )
    
    results = extract_data(pages=1)
    
    assert len(results) >= 3

    assert len(results) >= 3, f"Expected at least 3 products, but got {len(results)}"
    assert results[0]['title'] == "Test Product"
    assert results[0]['price_usd'] == 10.0
    assert results[0]['rating'] == 5.0
    assert results[0]['colors'] == 2
    assert results[0]['sizes'] == "S, M, L"
    assert results[0]['gender'] == 'men'
    assert isinstance(results[0]['timestamp'], str)

def test_scrape_products_http_error(mock_requests, caplog):
    mock_requests.get(
        "https://fashion-studio.dicoding.dev/",
        status_code=404
    )
    
    with caplog.at_level(logging.ERROR):
        results = extract_data(pages=1)

    assert len(results) == 0
    assert any("Failed to fetch" in record.msg or "404" in record.msg for record in caplog.records)

def test_scrape_products_timeout(mock_requests, caplog):
    mock_requests.get(
        "https://fashion-studio.dicoding.dev/",
        exc=requests.exceptions.ConnectTimeout
    )
    
    with caplog.at_level(logging.ERROR):
        results = extract_data(pages=1)

    assert len(results) == 0
    assert any("timeout" in record.msg.lower() or "Failed to fetch" in record.msg for record in caplog.records)

def test_scrape_products_invalid_parsing(mock_requests, caplog):
    mock_requests.get(
        "https://fashion-studio.dicoding.dev/",
        text="<html><body><div class='collection-card'></div></body></html>"
    )
    
    with caplog.at_level(logging.ERROR):
        results = extract_data(pages=1)

    assert len(results) == 0
    assert any(
        "Error parsing" in record.msg or "Missing" in record.msg or "invalid" in record.msg.lower()
        for record in caplog.records
    ) or len(results) == 0, "Harus skip produk kosong dan log error jika ada"

def test_scrape_products_main_function(capsys, monkeypatch):
    monkeypatch.setattr(extract, "extract_data", lambda pages=2: [{"title": "Sample"}])

    extract.main()

    captured = capsys.readouterr()
    assert "Berhasil scrape 1 produk" in captured.out
    assert "{'title': 'Sample'}" in captured.out