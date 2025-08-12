import requests
import json
from requests.auth import HTTPBasicAuth

# ----------------------------
# CONFIGURATION
# ----------------------------
ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'testmodule'
ODOO_USER = 'ankuxshh72@gmail.com'
ODOO_PASS = 'admin2025'

WC_BASE = "http://localhost/wordpress"
WC_CONSUMER_KEY = "ck_your_new_read_write_key"
WC_CONSUMER_SECRET = "cs_your_new_read_write_key"

JSONRPC_URL = ODOO_URL + '/jsonrpc'
WC_PRODUCTS_URL = f"{WC_BASE}/wp-json/wc/v3/products"

# ----------------------------
# Odoo Helpers
# ----------------------------
def odoo_jsonrpc(service, method, args, req_id=1):
    payload = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'service': service,
            'method': method,
            'args': args
        },
        'id': req_id
    }
    r = requests.post(JSONRPC_URL, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()

def login_odoo():
    res = odoo_jsonrpc('common', 'login', [ODOO_DB, ODOO_USER, ODOO_PASS], req_id=11)
    uid = res.get('result')
    if not uid:
        raise Exception('Odoo login failed: ' + json.dumps(res))
    return uid

def fetch_odoo_products(uid):
    fields = ['id', 'name', 'list_price', 'description_sale', 'qty_available']
    res = odoo_jsonrpc(
        'object', 'execute_kw',
        [ODOO_DB, uid, ODOO_PASS, 'product.template', 'search_read', 
         [[]], 
         {'fields': fields}],
        req_id=12
    )
    return res.get('result', [])

# ----------------------------
# WooCommerce Helpers
# ----------------------------
def get_wc_products():
    params = {
        'consumer_key': WC_CONSUMER_KEY,
        'consumer_secret': WC_CONSUMER_SECRET,
        'per_page': 100
    }
    r = requests.get(WC_PRODUCTS_URL, params=params)
    print(f"GET {r.url} -> {r.status_code}")
    if r.status_code != 200:
        print(f"Error: {r.text}")
    r.raise_for_status()
    return r.json()

def create_wc_product(product):
    payload = {
        'name': product.get('name'),
        'type': 'simple',
        'regular_price': str(product.get('list_price', 0) or 0),
        'description': product.get('description_sale') or '',
        'sku': f"ODOO-{product['id']}",
        'stock_quantity': int(product.get('qty_available') or 0),
        'manage_stock': True,
        'status': 'publish',
        'catalog_visibility': 'visible'
    }
    params = {
        'consumer_key': WC_CONSUMER_KEY,
        'consumer_secret': WC_CONSUMER_SECRET
    }
    
    print(f"Creating product: {payload['name']}")
    r = requests.post(
        WC_PRODUCTS_URL,
        headers={"Content-Type": "application/json"},
        params=params,
        json=payload
    )
    
    print(f"Response: {r.status_code} - {r.text}")
    if r.status_code == 201:
        return r.json()
    else:
        print(f"Failed to create {product['name']}: {r.status_code} - {r.text}")
        return None

# ----------------------------
# MAIN
# ----------------------------
if __name__ == '__main__':
    print("🔄 Logging into Odoo...")
    try:
        uid = login_odoo()
        print(f"✅ Logged in to Odoo as user {ODOO_USER} (uid={uid})")
    except Exception as e:
        print(f"❌ Odoo login failed: {e}")
        exit(1)

    print("📥 Fetching existing WooCommerce products...")
    try:
        wc_products = get_wc_products()
        wc_skus = {p.get('sku', '') for p in wc_products}
        print(f"✅ Found {len(wc_products)} products in WooCommerce.")
    except Exception as e:
        print(f"❌ Failed to fetch WooCommerce products: {e}")
        exit(1)

    print("📥 Fetching products from Odoo...")
    try:
        odoo_products = fetch_odoo_products(uid)
        print(f"✅ Found {len(odoo_products)} products in Odoo.")
    except Exception as e:
        print(f"❌ Failed to fetch Odoo products: {e}")
        exit(1)

    print("⬆️ Syncing to WooCommerce...")
    created = 0
    skipped = 0
    for p in odoo_products:
        odoo_sku = f"ODOO-{p['id']}"
        if odoo_sku in wc_skus:
            print(f"⏩ Skipping (already exists): {p['name']} [{odoo_sku}]")
            skipped += 1
        else:
            try:
                result = create_wc_product(p)
                if result:
                    print(f"✅ Created: {p['name']} (${p['list_price']}) Stock: {int(p['qty_available'])}")
                    created += 1
                else:
                    print(f"❌ Failed to create: {p['name']}")
            except Exception as e:
                print(f"❌ Error creating product {p['name']}: {e}")

    print(f"✅ Sync complete! Created: {created}, Skipped: {skipped}")
    print(f"👉 Visit your WooCommerce shop: {WC_BASE}/shop")