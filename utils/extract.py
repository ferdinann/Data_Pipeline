import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from typing import List, Dict
import time

# Mengatur sistem logging untuk mencatat proses scraping
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('scraper.log'), logging.StreamHandler()]
)

BASE_URL = "https://fashion-studio.dicoding.dev"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_page(page: int) -> requests.Response:
    """Mengambil konten satu halaman web dengan mekanisme retry sederhana"""
    if page == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}/page{page}"
    
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt == max_attempts:
                logging.error(f"Failed to fetch page {page} after {max_attempts} attempts: {str(e)}")
                raise
            wait_time = 2 ** attempt  # 2s, 4s, 8s
            logging.warning(f"Attempt {attempt} failed for page {page}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

def parse_product(product: BeautifulSoup) -> Dict | None:
    try:
        # Mencari elemen judul dengan beberapa kemungkinan tag dan class
        title_tag = (
            product.find("h3") or
            product.find("h4") or
            product.find("div", class_=lambda x: x and ("title" in x or "name" in x)) or
            product.find("a", class_=lambda x: x and ("title" in x or "name" in x))
        )

        price_tag = (
            product.find("span", class_=lambda x: x and "price" in x.lower()) or
            product.find("p", class_=lambda x: x and "price" in x.lower()) or
            product.find(string=lambda s: s and "$" in (s or ""))
        )

        rating_tag = (
            product.find(string=lambda s: s and ("rating" in (s or "").lower() or "⭐" in (s or ""))) or
            product.find("span", class_=lambda x: x and "rating" in x.lower())
        )
        # Mencari info warna, ukuran, dan gender (jika ada)
        colors_tag = product.find(string=lambda s: s and "colors" in (s or "").lower())
        size_tag   = product.find(string=lambda s: s and "size:" in (s or "").lower())
        gender_tag = product.find(string=lambda s: s and "gender:" in (s or "").lower())

        if not title_tag or not price_tag:
            raise ValueError("Missing title or price element")

        title = title_tag.get_text(strip=True)

        # Membersihkan dan mengonversi harga menjadi angka
        price_text = price_tag.get_text(strip=True) if price_tag else ""
        price_text = price_text.replace("$", "").replace(",", "").strip()
        try:
            price = float(price_text)
        except ValueError:
            price = 0.0

        # Membersihkan dan mengonversi rating menjadi angka
        rating_text = rating_tag.get_text(strip=True) if rating_tag else "0"
        rating_parts = [p.strip() for p in rating_text.replace("⭐", "").split("/") if p.strip()]
        rating_str = rating_parts[-1] if rating_parts else "0"
        try:
            rating = float(rating_str)
        except ValueError:
            rating = 0.0

        # Mengambil jumlah warna (hanya angka)
        colors_text = colors_tag.strip() if colors_tag else "0 colors"
        colors_str = ''.join(c for c in colors_text if c.isdigit())
        colors = int(colors_str) if colors_str else 0

        # Mengambil informasi ukuran dan gender
        sizes = size_tag.strip().split(":", 1)[-1].strip() if size_tag else "Unknown"
        gender = gender_tag.strip().split(":", 1)[-1].strip().lower() if gender_tag else "unknown"

        return {
            "title": title,
            "price_usd": price,
            "rating": rating,
            "colors": colors,
            "sizes": sizes,
            "gender": gender,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.debug(f"Error parsing one product: {str(e)}")
        return None

def extract_data(pages: int = 50) -> List[Dict]:
    """Melakukan scraping data produk dari semua halaman yang ditentukan"""
    logging.info("Starting scraping process")
    all_products = []

    for page in range(1, pages + 1):
        try:
            response = fetch_page(page)
            soup = BeautifulSoup(response.content, "html.parser")

            # Daftar selector alternatif untuk menemukan container produk
            possible_selectors = [
                ("div", {"class": lambda x: x and ("product" in x.lower() or "card" in x.lower() or "item" in x.lower())}),
                ("div", {"class": "collection-card"}),
                ("div", {"class": "col-md-3"}),
                ("div", {"class": "product-item"}),
            ]

            products = []
            for tag, attrs in possible_selectors:
                candidates = soup.find_all(tag, attrs)
                if candidates:
                    products = candidates
                    logging.info(f"Page {page}: Found {len(products)} items using selector '{tag}' with attrs {attrs}")
                    break

            if not products:
                logging.warning(f"No products found on page {page}")
                if page > 5:  # Hentikan jika beberapa halaman terakhir kosong
                    logging.info("Mungkin sudah akhir halaman. Berhenti scraping.")
                    break
                continue

            page_products = 0
            for product in products:
                parsed = parse_product(product)
                if parsed:
                    all_products.append(parsed)
                    page_products += 1

            logging.info(f"Page {page} berhasil: {page_products} produk valid dari {len(products)} item")

        except Exception as e:
            logging.error(f"Critical error on page {page}: {str(e)}")
            break

    logging.info(f"Scraping selesai. Total produk: {len(all_products)}")
    return all_products

def main():
    """Fungsi utama untuk menjalankan proses scraping (mode test dengan halaman terbatas)"""
    # Jalankan tes dengan jumlah halaman kecil terlebih dahulu
    test_data = extract_data(pages=5)
    print(f"Berhasil scrape {len(test_data)} produk")
    
    if test_data:
        print("\nContoh produk pertama:")
        print(test_data[0])
    else:
        print("Tidak ada produk yang berhasil di-scrape. Periksa selector HTML di situs.")

if __name__ == "__main__":
    main()