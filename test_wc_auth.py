import requests

# --- CONFIG ---
WC_BASE = "http://localhost/wordpress"
WC_CONSUMER_KEY = "ck_15edb3e5f6ff39dd35f87a9a0ec076ff1bca6890"
WC_CONSUMER_SECRET = "cs_84d90dd251008102e78e0e3111dc03b190957f29"

# --- TEST GET PRODUCTS ---
url = f"{WC_BASE}/wp-json/wc/v3/products"
r = requests.get(url, auth=(WC_CONSUMER_KEY, WC_CONSUMER_SECRET))

print("Status code:", r.status_code)
print("Response:", r.text)
