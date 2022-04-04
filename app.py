from flask import Flask, request, Response
import json
import sqlite3
import datetime as dt
app = Flask(__name__)

DATABASE = "database/student_records.db"
DATA_SKELETON = {"first_name": str, "last_name": str, "dob": str, "amount_due": float}


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/create/', methods=["POST"])
def create_record():
    request_data = dict(request.args)
    # return app.response_class(json.dumps({"error_message": request_data}), status=400, mimetype='application/json')
    expected_keys = set(DATA_SKELETON.keys())
    received_keys = set(request_data.keys())
    if expected_keys != received_keys:
        a = received_keys - expected_keys
        if len(a) > 0:
            return app.response_class(json.dumps({"error_message": "Unexpected key(s): {}".format(", ".join(list(a)))}), status=400, mimetype='application/json')
        b = expected_keys - received_keys
        if len(b) > 0:
            return app.response_class(json.dumps({"error_message": "Missing key(s): {}".format(", ".join(list(b)))}), status=400, mimetype='application/json')
    """for key, value in DATA_SKELETON.items():
        if not isinstance(request_data[key], value):
            
            return app.response_class(json.dumps({"error_message": "{} expects {} received {}".format(key, value, type(request_data[key]))}), status=400, mimetype='application/json')"""
    request_data['amount_due'] = float(request_data['amount_due'])
    try:
        checking_date = dt.datetime.strptime(request_data['dob'], "%Y-%m-%d")
    except:
        return app.response_class(response=json.dumps({"error_message": "dob expects YYYY-MM-DD format"}), status=344, mimetype='application/json')
    try:
        with sqlite3.connect(DATABASE, isolation_level='EXCLUSIVE', timeout=10) as connection:
            db = connection.cursor()
            db.execute("""INSERT INTO 'student_info' ('first_name','last_name','dob','amount_due') VALUES('{}','{}','{}',{});""".format(request_data['first_name'], request_data['last_name'], request_data['dob'], request_data['amount_due']))
        return app.response_class(response=json.dumps({"message": "New Record Created"}), status=201, mimetype='application/json')
    except Exception as e:
        return app.response_class(response=json.dumps({"error_message": "Error Creating New Record", "execption": str(e)}), status=344, mimetype='application/json')


@app.route('/read', methods=["GET"])
def read_record():
    return app.response_class(response=json.dumps({"test": "hgbjhlsdgj"}), status=200, mimetype='application/json')


@app.route('/update', methods=["PUT"])
def update_record():
    return 'Hello World!'


@app.route('/delete', methods=["DELETE"])
def delete_record():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host="127.0.0.2", port=9000, debug=True)
