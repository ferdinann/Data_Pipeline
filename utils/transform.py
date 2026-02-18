import pandas as pd
import logging
from typing import List, Dict

# Mengatur konfigurasi logging dasar untuk mencatat proses transformasi
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def transform_data(raw_data: List[Dict]) -> pd.DataFrame:
    """Membersihkan dan mentransformasi list data produk mentah menjadi DataFrame yang siap analisis"""
    if not isinstance(raw_data, list):
        raise ValueError("Input must be a list of dictionaries")

    cleaned_data = []
    # Kurs konversi USD ke IDR (nilai tetap untuk transformasi)
    usd_to_idr = 16000

    for product in raw_data:
        try:
            required = ['title', 'price_usd', 'rating', 'colors', 'sizes', 'gender', 'timestamp']
            if not all(key in product for key in required):
                raise ValueError("Missing required fields")
                # Mengatur konfigurasi logging dasar untuk mencatat proses transformasi
            if product['title'] in ["Unknown Product", "Price Unavailable", "Invalid Rating", None]:
                continue

            try:
                price_idr = float(product['price_usd']) * usd_to_idr
                rating = float(product['rating'])
            except (ValueError, TypeError):
                raise ValueError("Invalid price or rating value")

            if isinstance(product['sizes'], str):
                size_text = product['sizes'].split(':')[-1].strip()
            elif isinstance(product['sizes'], list):
                size_text = ','.join(product['sizes'])
            else:
                size_text = ""

            if isinstance(product['gender'], str):
                gender = product['gender'].lower().replace("gender:", "").strip()
            else:
                gender = ""

            colors_raw = product['colors']
            if isinstance(colors_raw, (list, tuple)):
                color_count = len(colors_raw)
            elif isinstance(colors_raw, int):
                color_count = colors_raw
            elif isinstance(colors_raw, str):
                try:
                    color_count = int(colors_raw.strip().split()[0])
                except Exception:
                    color_count = 0
            else:
                color_count = 0

            cleaned_data.append({
                'title': str(product['title']),
                'price_idr': round(price_idr, 2),
                'rating': rating,
                'colors': color_count,
                'sizes': size_text,
                'gender': gender,
                'timestamp': product['timestamp']
            })

        except (KeyError, ValueError, TypeError) as e:
            logging.warning(f"Skipping invalid product: {str(e)}")
            continue
        except Exception as e:
            logging.error(f"Unexpected error transforming product: {str(e)}")
            continue

    df = pd.DataFrame(cleaned_data)

    if df.empty:
        return df

    df = df.dropna()
    df = df.drop_duplicates(subset=['title', 'price_idr'])

    df = df[
        (df['title'] != "") &
        (df['price_idr'] > 0) &
        (df['rating'].between(0, 5)) &
        (df['colors'] > 0) &
        (df['sizes'] != "") &
        (df['gender'].isin(['men', 'women', 'unisex']))
    ]

    df = df.astype({
        'title': 'string',
        'price_idr': 'float64',
        'rating': 'float64',
        'colors': 'int64',
        'sizes': 'string',
        'gender': 'category'
    })

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    return df.reset_index(drop=True)

if __name__ == "__main__":
    test_data = [
        {
            'title': 'Test Product',
            'price_usd': 10.0,
            'rating': 4.5,
            'colors': ['red', 'blue'],
            'sizes': 'Size: S,M,L',
            'gender': 'Gender: Men',
            'timestamp': '2025-05-03T00:00:00'
        }
    ]

    try:
        df = transform_data(test_data)
        print("Transformation test successful!")
        print(df.head())
    except Exception as e:
        print(f"Transformation test failed: {str(e)}")