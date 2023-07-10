from flask import Flask, request
import flask
from flask_cors import CORS
from flask_basicauth import BasicAuth
import modified_gmm
import json
import requests
import schedule
import time
import threading

app = Flask(__name__)
CORS(app)

app.config['BASIC_AUTH_USERNAME'] = 'username'
app.config['BASIC_AUTH_PASSWORD'] = 'password'

basic_auth = BasicAuth(app)

class cache:

    def __init__(self):

        self.orders = None
        self.count = 0

        self.store = set()

    def clear_store(self):
        self.store.clear()


val_cache = cache()

def clear_store_at_midnight():
    val_cache.clear_store()



def get_all_orders():

    url = 'https://ssapi.shipstation.com/orders?orderStatus=awaiting_shipment'

    username = 'usernamr'
    password = 'password'

    page = 1
    has_next_page = True

    all_orders = []

    tmp_count = 0

    print("okay")

    while has_next_page:

        params = { 'page':page }

        response = requests.get(url, params=params, auth=(username, password))

        if response.status_code == 200:

            data = response.json()
            every_orders = data['orders']
            all_orders.extend(data['orders'])
            has_next_page = data['pages'] > page
            page += 1


            for each in every_orders:

                for each_item in each["items"]:

                    val_cache.count += int(each_item["quantity"])

                    tmp_count+=int(each_item["quantity"])


        else:
            print(f"Error retrieving orders from page {page}: {response.status_code}")


    val_cache.orders = all_orders

    print(tmp_count)



@app.route('/test', methods=["GET"])
@basic_auth.required
def test():

    return "WORKS"




@app.route('/get_orders', methods=["GET"])
@basic_auth.required
def all_orders():

    print("OKOK")

    val_cache.orders = None
    val_cache.count = 0

    get_all_orders()

    print(val_cache.count)

    
    return str(val_cache.count)


@app.route('/', methods=['POST'])
@basic_auth.required
def process_selections():

    people_wraps = []

    selections = request.json
    for selection in selections:

        each_detail = []

        name = selection['name']
        userId = selection['userId']
        wrapCount = selection['wrapCount']

        each_detail.append(userId)
        each_detail.append(wrapCount)

        people_wraps.append(each_detail)

    print("finding....")

    if val_cache.orders != None:

        print("cache_full")

        final_cluster = modified_gmm.algo(val_cache.orders, people_wraps, val_cache)

    else:

        print("cache_empty")

        get_all_orders()

        final_cluster = modified_gmm.algo(val_cache.orders, people_wraps, val_cache)

    print(final_cluster)

    # url = 'https://ssapi.shipstation.com/orders/assignuser'

    # username = 'username'
    # password = 'password'

    # for key,value in final_cluster.items():

    #     print(key)
    #     print(value)

    #     payload = {
    #         "orderIds": [523437759,523437760],
    #         "userId": "f7d1cc39-a7da-4788-8005-9dba88b6e6af"
    #     }

    #     headers = {
    #     'Content-Type': 'application/json'
    #     }


    #     response = requests.post(url, auth=(username, password), data=json.dumps(payload), headers=headers)

    #     print(response.status_code)
    #     print(response.json())

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
