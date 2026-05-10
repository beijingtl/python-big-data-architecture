"""
Flask APP

set FLASK_APP=C:/Users/14606/Desktop/写书/writing_related/message_queue/code/simple_user_behavior_data_collection/app.py
set FLASK_ENV=development
# powershell
$env:FLASK_ENV = "development"
"""
from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("base.html", title="首页")

@app.route('/detail')
def detail():
    return render_template("base.html", title="产品详情页")

@app.route('/cart')
def cart():
    return render_template("base.html", title="购物车页")

import json
from flask import Flask, request
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['192.168.0.52:32769', '192.168.0.52:32770'])

@app.route('/api/collect/')
def collect_to_kafka():
    _collection_data = {i:request.args[i] for i in request.args}
    _collection_data["ua"] = request.headers["User-Agent"]
    producer.send("collection", json.dumps(_collection_data).encode("utf-8"))
    producer.flush()
    return "OK!"