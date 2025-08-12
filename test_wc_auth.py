import requests
from requests.auth import HTTPBasicAuth

# WooCommerce config
WC_BASE = "http://localhost/wordpress"
WC_CONSUMER_KEY = "ck_e7682340d7dba06e5c63ccd9bf862118ac7b15f7"
WC_CONSUMER_SECRET = "cs_76a910136ac2c7d9353c0bb28cb694a9f4543ac1"

def test_wc_connection():
    print("🔍 Testing WooCommerce API connection...")

    try:
        r = requests.get(
            WC_BASE,
            auth=HTTPBasicAuth(WC_CONSUMER_KEY, WC_CONSUMER_SECRET),
            params={"per_page": 1}  # limit results for test
        )

        print(f"Status code: {r.status_code}")
        print("Response:", r.text)

        if r.status_code == 200:
            print("✅ WooCommerce connection successful!")
        else:
            print("❌ WooCommerce connection failed. Check API keys, .htaccess, and Apache config.")

    except Exception as e:
        print("🚫 Error:", str(e))

if __name__ == "__main__":
    test_wc_connection()
