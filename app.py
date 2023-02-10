"""
Fitness Data Tracker
"""

import json
import os

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra import DriverException
from cassandra import RequestExecutionException
from flask import Flask, request, jsonify
from utils.logger import get_logger

import data.fetch
import data.initialize
import data.update

app = Flask(__name__)

logger = get_logger('default')

keyspace = os.environ['KEYSPACE']

cloud_config= {
  'secure_connect_bundle': '/bundles/secure-connect-cassandra-db-1.zip'
}
client_id_cred_file = open('/bundles/client_id.txt', 'r')
client_id = client_id_cred_file.read()
client_id_cred_file.close()
client_secret_cred_file = open('/bundles/client_secret.txt', 'r')
client_secret = client_secret_cred_file.read()
client_secret_cred_file.close()

auth_provider = PlainTextAuthProvider(client_id, client_secret)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect(keyspace)

data.initialize.create_tables(session)

@app.route('/health/ready')
def health():
    """Health check"""
    row = session.execute("select release_version from system.local").one()
    if row:
        return jsonify({"status": "UP"})
    return jsonify({
        "message": "error occurred - verify Cassandra connectivity"
    }), 502

@app.route('/add/activity', methods=['PUT'])
def add_daily_activity():
    """Add daily activity data"""
    records = json.loads(request.data)
    res = data.update.add_activity_data(session, records)
    if res == 1:
        return jsonify({
            "message": "successfully added daily fitness data record"
        }), 201
    return jsonify({
        "message": "an error occurred adding fitness data"
    }), 500

@app.route('/add/sleep', methods=['PUT'])
def add_daily_sleep():
    """Add daily sleep data"""
    records = json.loads(request.data)
    res = data.update.add_sleep_data(session, records)
    if res == 1:
        return jsonify({
            "message": "successfully added daily sleep data record"
        }), 201
    return jsonify({
        "message": "an error occurred adding sleep data"
    }), 500

@app.route('/add/weight', methods=['PUT'])
def add_daily_weight():
    """Add daily weight data"""
    records = json.loads(request.data)
    res = data.update.add_weightloss_data(session, records)
    if res == 1:
        return jsonify({
            "message": "successfully added daily weight data record"
        }), 201
    return jsonify({
        "message": "an error occurred adding weight data"
    }), 500

@app.route('/<uid>/<tracker>', methods=['GET'])
def get_activity(uid, tracker):
    """Get most active days"""
    try:
        days = data.fetch.get_activity(session, uid, tracker)
    except (DriverException, RequestExecutionException) as err:
        logger.error(err)
        return jsonify({
            "message": "error fetching user data"
        }), 500
    if len(days['days']) == 0:
        return jsonify({
            "message": "user not found"
        }), 404
    return days, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
