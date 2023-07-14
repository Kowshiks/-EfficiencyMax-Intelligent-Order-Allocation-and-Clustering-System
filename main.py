from flask import Flask, request
import flask
from flask_cors import CORS
from flask_basicauth import BasicAuth
import clustering_algo
import json
import requests
import schedule
import time
import threading

app = Flask(__name__)
CORS(app)

app.config['BASIC_AUTH_USERNAME'] = 'kowshik_test'
app.config['BASIC_AUTH_PASSWORD'] = 'kowshik_test'

basic_auth = BasicAuth(app)

class products_class:

    def __init__(self):

        self.total_products = None

        self.count = 0

        self.store = set()

    def clear_store(self):
        self.store.clear()


product_cache = products_class()

def clear_store_at_midnight():

    product_cache.clear_store()


def get_all_orders():

    url = 'API TO GET PRODUCTS'

    username = 'username'
    password = 'password'

    page = 1

    next_page = True

    products = []

    product_count = 0

    while next_page:

        params = { 'page':page }

        response = requests.get(url, params=params, auth=(username, password))

        if response.status_code == 200:

            data = response.json()

            indiv_order = data['val']
            products.extend(data['val'])

            next_page = data['pages'] > page
            page += 1


            for each in indiv_order:

                for each_item in each["val"]:

                    product_cache.count += int(each_item["val"])

                    product_count+=int(each_item["val"])


        else:
            print(f"Error retrieving products from page {page}: {response.status_code}")


    product_cache.total_products = products

    print(product_count)


@app.route('/get_products', methods=["GET"])
@basic_auth.required
def get_products():

    product_cache.total_products = None
    product_cache.count = 0

    get_all_orders()
    
    return str(product_cache.count)


@app.route('/', methods=['POST'])
@basic_auth.required
def assign_function():

    assign_product = []

    selections = request.json
    for selection in selections:

        all_details = []

        name = selection['memeberName']
        userId = selection['memberId']

        act_count = selection['productCount']

        all_details.append(userId)
        all_details.append(act_count)

        assign_product.append(all_details)

    if product_cache.total_products != None:

        final_cluster = clustering_algo.gmm_algo(product_cache.total_products, assign_product, product_cache)

    else:

        get_all_orders()

        final_cluster = clustering_algo.gmm_algo(product_cache.total_products, assign_product, product_cache)


    url = 'ASSIGN USER API'

    username = 'username'
    password = 'password'

    for key,value in final_cluster.items():

        payload = {
            "orderIds": [],
            "userId": "userId"
        }

        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.post(url, auth=(username, password), data=json.dumps(payload), headers=headers)

    return "Done"

schedule.every().day.at('00:00').do(clear_store_at_midnight)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
        
if __name__ == '__main__':

    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()


    app.run(host="0.0.0.0",port=int(8080),debug=True)

