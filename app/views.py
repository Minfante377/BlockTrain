import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
MAX_LOADS = 50
errors = None
values = None
error_id = "#E2E5E2"

def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address, json = json_object)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    global errors
    global values
    #fetch_posts()
    error = ["#E2E5E2","#E2E5E2","#E2E5E2"]
    value = ['','','']
    if not errors:
        errors = []
        values = []
        for i in range(MAX_LOADS):
            errors.append(error)
            values.append(value)
    return render_template('index.html',
                           title='BlockTrain: Seguimiento descentralizado de cargas',
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string, errors = errors, values = values, MAX_LOADS = MAX_LOADS, error_id = error_id)

@app.route('/analize', methods=['POST'])
def analize():
    global errors
    global values
    global error_id
    _id = request.form['order_id']
    companies = []
    ids = []
    loads = []
    for i in range (MAX_LOADS):
        companies.append(request.form['company_'+str(i)])
        ids.append(request.form['id_'+str(i)])
        loads.append(request.form['load_'+str(i)])
    endpoint = "{}/get_last_block".format(CONNECTED_NODE_ADDRESS)
    print(endpoint)
    json_object = {'ID' : _id} 
    check_adress = "{}/check_id".format(CONNECTED_NODE_ADDRESS)
    response = requests.post(check_adress,json = json_object)
    if not response:
        error_id = "#F72E03"
        return redirect("/")
    error_id = "#E2E5E2"
    errors = []
    values = []
    response = requests.get(endpoint, json = json_object)
    block_chain = json.loads(response.content)['block']
    tx = block_chain['transactions'][-1]['content']
    previous_companies = tx[0]
    previous_ids = tx[1]
    previous_loads = tx[2]
    i = 0
    error = []
    while i < MAX_LOADS:
        if not previous_companies[i] == '': 
            value = [companies[i], ids[i], loads[i]]
            if not companies[i] == previous_companies[i]:
                print("%s vs %s" %(companies[i], previous_companies[i]))
                error.append("#F72E03")
            else:
                error.append("#3AF703")
            if not ids[i] == previous_ids[i]:
                error.append("#F72E03")
            else:
                error.append("#3AF703")
            if not loads[i] == previous_loads[i]:
                print("%s vs %s" %(loads[i], previous_loads[i]))
                error.append("#F72E03")
            else:
                error.append("#3AF703")
        else:
            error = ["#E2E5E2","#E2E5E2","#E2E5E2"]
            value = ['','','']
        errors.append(error)
        values.append(value)
        error = []
        value = []
        i = i+1
    print(errors)
    return redirect("/")
        


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    global errors
    global error_id
    companies = []
    ids = []
    loads = []
    for i in range (50):
        companies.append(request.form['company_'+str(i)])
        ids.append(request.form['id_'+str(i)])
        loads.append(request.form['load_'+str(i)])
    content = (companies, ids, loads)
    _id = request.form["location_id"]

    post_object = {
        'ID': _id,
        'content': content,
    }

    check_adress = "{}/check_id".format(CONNECTED_NODE_ADDRESS)
    response = requests.post(check_adress,json = post_object)
    if not response:
        error_id = "#F72E03"
        return redirect("/")
    error_id = "#E2E5E2"
    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})
    #Mine new transaction
    mine_address = "{}/mine".format(CONNECTED_NODE_ADDRESS)
    requests.get(mine_address, json = post_object)
    errors = None
    return redirect('/')

@app.route('/new_chain', methods = ['POST'])
def new_chain():
    global errors
    global error_id
    error_id = "#E2E5E2"
    _id = request.form['order_id']
    json_object = {'ID': _id}
    new_chain_address = "{}/new_chain".format(CONNECTED_NODE_ADDRESS) 
    requests.post(new_chain_address,
                  json=json_object,
                  headers={'Content-type': 'application/json'})
    companies = []
    ids = []
    loads = []
    for i in range (50):
        companies.append(request.form['company_'+str(i)])
        ids.append(request.form['id_'+str(i)])
        loads.append(request.form['load_'+str(i)])
    content = (companies, ids, loads)

    post_object = {
        'ID': _id,
        'content': content,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})
    #Mine new transaction
    mine_address = "{}/mine".format(CONNECTED_NODE_ADDRESS)
    requests.get(mine_address, json = post_object)
    errors = None
    return redirect('/')
def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
