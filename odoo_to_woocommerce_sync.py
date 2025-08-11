import requests
import json
from requests.auth import HTTPBasicAuth

# ---------- CONFIG ----------
ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'testmodule'
ODOO_USER = 'ankuxshh72@gmail.com'
ODOO_PASS = 'admin2025'

WC_BASE = "http://localhost/wordpress"
WC_CONSUMER_KEY = "ck_0e1f95fce66a82088b447342158d6aa9180691aa"
WC_CONSUMER_SECRET = "cs_01e0abf3a17309de5edb936085b3f176f682510c"
# ----------------------------

JSONRPC_URL = ODOO_URL + '/jsonrpc'
WC_PRODUCTS_URL = f"{WC_BASE}/wp-json/wc/v3/products"

# ----------------------------
# Odoo JSON-RPC Helper
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

def fetch_odoo_products(uid, limit=10):
    fields = ['id', 'name', 'list_price', 'description_sale', 'qty_available']
    res = odoo_jsonrpc(
        'object', 'execute_kw',
        [ODOO_DB, uid, ODOO_PASS, 'product.template', 'search_read', [[]], {'fields': fields, 'limit': limit}],
        req_id=12
    )
    return res.get('result', [])

# ----------------------------
# WooCommerce Helpers
# ----------------------------
def create_wc_product(product):
    payload = {
        'name': product.get('name') or 'Unnamed',
        'type': 'simple',
        'regular_price': str(product.get('list_price', 0) or 0),
        'description': product.get('description_sale') or '',
        'stock_quantity': int(product.get('qty_available') or 0),
        'manage_stock': True
    }
    r = requests.post(WC_PRODUCTS_URL, auth=HTTPBasicAuth(WC_CONSUMER_KEY, WC_CONSUMER_SECRET), json=payload)
    if r.status_code == 201:
        print(f"✅ Created WC product: {product['name']}")
        return r.json()
    else:
        print(f"❌ Failed to create {product['name']} - {r.status_code} - {r.text}")
        return None

def fetch_wc_products():
    r = requests.get(WC_PRODUCTS_URL, auth=HTTPBasicAuth(WC_CONSUMER_KEY, WC_CONSUMER_SECRET))
    if r.status_code == 200:
        products = r.json()
        print(f"\n📦 WooCommerce Products ({len(products)})")
        for p in products:
            print(f"- {p['id']}: {p['name']} (${p['price']})")
    else:
        print(f"❌ Failed to fetch WC products: {r.status_code} - {r.text}")

# ----------------------------
# Main Script
# ----------------------------
if __name__ == '__main__':
    uid = login_odoo()
    odoo_products = fetch_odoo_products(uid, limit=5)
    print(f"Found {len(odoo_products)} products in Odoo.")

    for p in odoo_products:
        create_wc_product(p)

    fetch_wc_products()
