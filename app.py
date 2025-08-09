from flask import Flask, request, jsonify
from flask_cors import CORS
import xmlrpc.client

app = Flask(__name__)
CORS(app)  

# Odoo connection config
ODOO_URL = "http://localhost:8069"
ODOO_DB = "testmodule"
ODOO_USERNAME = "ankuxshh72@gmail.com"
ODOO_PASSWORD = "admin2025"

@app.route('/odoo-contact-api', methods=['GET', 'POST'])
def create_contact():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        message = data.get('message', '')

        # Authenticate with Odoo
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

        # Create contact (res.partner)
        contact_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'create',
            [{
                'name': name,
                'email': email,
                'phone': phone,
                'comment': message
            }]
        )

        return jsonify({'status': 'success', 'contact_id': contact_id})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
