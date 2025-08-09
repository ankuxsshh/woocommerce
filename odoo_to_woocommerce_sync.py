import requests
import json

# ---------- CONFIG ----------
ODOO_URL = 'http://localhost:8069'   # Odoo base
ODOO_DB  = 'testmodule'              # Your Odoo database
ODOO_USER = 'ankuxshh72@gmail.com'   # Your Odoo username (email)
ODOO_PASS = 'admin2025'              # Your Odoo password

WC_BASE = 'http://localhost/wordpress'  # Your WordPress site base URL
WC_CONSUMER_KEY = 'ck_15edb3e5f6ff39dd35f87a9a0ec076ff1bca6890'
WC_CONSUMER_SECRET = 'cs_84d90dd251008102e78e0e3111dc03b190957f29'
# ----------------------------

JSONRPC_URL = ODOO_URL + '/jsonrpc'

def odoo_jsonrpc(service, method, args, req_id=1):
    """Send a JSON-RPC request to Odoo."""
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

def login():
    """Login to Odoo and return the user ID."""
    res = odoo_jsonrpc('common', 'login', [ODOO_DB, ODOO_USER, ODOO_PASS], req_id=11)
    uid = res.get('result')
    if not uid:
        raise Exception('Odoo login failed: ' + json.dumps(res))
    return uid

def fetch_products(uid, limit=10):
    """Fetch product data from Odoo."""
    fields = ['id', 'name', 'list_price', 'description_sale', 'qty_available']
    res = odoo_jsonrpc(
        'object', 'execute_kw',
        [ODOO_DB, uid, ODOO_PASS, 'product.template', 'search_read',
         [[]], {'fields': fields, 'limit': limit}],
        req_id=12
    )
    return res.get('result', [])

from requests.auth import HTTPBasicAuth

def create_wc_product(product):
    url = f"{WC_BASE}/wp-json/wc/v3/products"

    payload = {
        'name': product.get('name') or 'Unnamed',
        'type': 'simple',
        'regular_price': str(product.get('list_price', 0) or 0),
        'description': product.get('description_sale') or '',
        'stock_quantity': int(product.get('qty_available') or 0),
        'manage_stock': True
    }

    r = requests.post(url, json=payload, auth=HTTPBasicAuth(WC_CONSUMER_KEY, WC_CONSUMER_SECRET))

    if r.status_code not in (200, 201):
        print(f"[ERROR] WooCommerce API returned {r.status_code}: {r.text}")
        r.raise_for_status()

    return r.json()

def test_wc_connection():
    """Test WooCommerce API connection before syncing products."""
    print("Testing WooCommerce connection...")
    url = f"{WC_BASE}/wp-json/wc/v3/products"
    auth = (WC_CONSUMER_KEY, WC_CONSUMER_SECRET)
    
    try:
        r = requests.get(url, auth=auth, params={'per_page': 1})
        print(f"Connection test status: {r.status_code}")
        
        if r.status_code == 200:
            print("✅ WooCommerce connection successful!")
        else:
            print(f"❌ Connection test failed: {r.text}")
    except Exception as e:
        print(f"🚫 Connection test error: {str(e)}")

def main():
    uid = login()
    products = fetch_products(uid, limit=20)
    print(f"Found {len(products)} products in Odoo.")

    for i, p in enumerate(products, 1):
        try:
            wc_product = create_wc_product(p)
            print(f"({i}/{len(products)}) Created WC product: {wc_product.get('id')} => {wc_product.get('name')}")
        except Exception as e:
            print(f"⚠️ Failed to create product {p.get('name')}: {str(e)}")

if __name__ == '__main__':
    test_wc_connection()  # Test connection first
    main()