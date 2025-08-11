import requests
from requests.auth import HTTPBasicAuth

# WooCommerce config
WC_BASE = "http://localhost/wordpress"
WC_CONSUMER_KEY = "ck_0e1f95fce66a82088b447342158d6aa9180691aa"
WC_CONSUMER_SECRET = "cs_01e0abf3a17309de5edb936085b3f176f682510c"

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
