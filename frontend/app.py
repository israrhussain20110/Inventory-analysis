from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

BACKEND_URL = "http://127.0.0.1:8000"

@app.route('/')
def index():
    try:
        response = requests.get(f"{BACKEND_URL}/inventory/metrics")
        response.raise_for_status()  # Raise an exception for bad status codes
        metrics = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching metrics: {e}")
        metrics = {}

    return render_template('index.html', metrics=metrics)

@app.route('/inventory')
def inventory():
    sort_by = request.args.get('sort_by', 'ProductID')
    sort_order = request.args.get('sort_order', 'asc')
    category = request.args.get('category')
    abc_class = request.args.get('abc_class')

    try:
        response = requests.get(f"{BACKEND_URL}/inventory/all")
        response.raise_for_status()
        inventory_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching inventory: {e}")
        inventory_data = []

    # Filtering
    if category:
        inventory_data = [item for item in inventory_data if item.get('category') == category]
    if abc_class:
        inventory_data = [item for item in inventory_data if item.get('abc_class') == abc_class]

    # Sorting
    if inventory_data:
        inventory_data = sorted(inventory_data, key=lambda x: x.get(sort_by, 0), reverse=sort_order == 'desc')

    return render_template('inventory.html', inventory=inventory_data, sort_by=sort_by, sort_order=sort_order)

@app.route('/product/<product_id>')
def product_detail(product_id):
    try:
        # Fetch all inventory data
        inventory_response = requests.get(f"{BACKEND_URL}/inventory/all")
        inventory_response.raise_for_status()
        all_inventory_data = inventory_response.json()

        # Filter for the specific product
        historical_inventory = [item for item in all_inventory_data if item.get('ProductID') == product_id]
        product = next((item for item in historical_inventory if item.get('ProductID') == product_id), None)


        # Fetch product metrics
        metrics_response = requests.get(f"{BACKEND_URL}/inventory/metrics?product_id={product_id}")
        metrics_response.raise_for_status()
        metrics = metrics_response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching product details: {e}")
        product = None
        metrics = {}
        historical_inventory = []

    return render_template('product_detail.html', product=product, metrics=metrics, historical_inventory=historical_inventory)

@app.route('/slow_movers')
def slow_movers():
    slow_turnover_threshold = request.args.get('slow_turnover_threshold', 2.0, type=float)
    dos_threshold = request.args.get('dos_threshold', 180, type=int)
    inactivity_days = request.args.get('inactivity_days', 180, type=int)

    try:
        response = requests.get(
            f"{BACKEND_URL}/inventory/slow_movers",
            params={
                "slow_turnover_threshold": slow_turnover_threshold,
                "dos_threshold": dos_threshold,
                "inactivity_days": inactivity_days,
            },
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching slow movers: {e}")
        data = {"slow_movers": [], "obsolete_items": []}

    return render_template('slow_movers.html', data=data, slow_turnover_threshold=slow_turnover_threshold, dos_threshold=dos_threshold, inactivity_days=inactivity_days)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        collection_name = request.form['collection_name']
        if file:
            files = {'file': (file.filename, file.stream, file.mimetype)}
            response = requests.post(f"{BACKEND_URL}/data/upload/{collection_name}", files=files)
            if response.status_code == 200:
                return redirect(url_for('inventory'))
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
