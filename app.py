from typing import Type
from flask import Flask, request, Response
import json
import sqlite3
import datetime as dt

app = Flask(__name__)

DATABASE = "database/student_records.db"
DATA_SKELETON = {"first_name": str, "last_name": str, "dob": str, "amount_due": float}


@app.route('/')
def index():
    return app.response_class(json.dumps({"apis": [{"create": {"data": "DATA_SKELETON", "method": [""]}},
                                                   {"read": {"data": {"student_id": ["*(for all records)", "integer"]},
                                                             "method": ["POST", "GET"]}},
                                                   {"update": {"data": {"student_id": "int",
                                                                        "*fields_to_be_modified": "new values"},
                                                               "method": ["PUT"]}},
                                                   {"delete": {"data": {"student_id": "int", "method": ["DELETE"]}}}
                                                   ]}), status=200, mimetype='application/json')


@app.route('/create', methods=["POST"])
def create_record():
    request_data = dict(request.args)
    expected_keys = set(DATA_SKELETON.keys())
    received_keys = set(request_data.keys())
    if expected_keys != received_keys:
        a = received_keys - expected_keys
        if len(a) > 0:
            return app.response_class(json.dumps({"error_message": "Unexpected key(s): {}".format(", ".join(list(a)))}),
                                      status=400, mimetype='application/json')
        b = expected_keys - received_keys
        if len(b) > 0:
            return app.response_class(json.dumps({"error_message": "Missing key(s): {}".format(", ".join(list(b)))}),
                                      status=400, mimetype='application/json')

    try:
        request_data['amount_due'] = float(request_data['amount_due'])
    except:
        return app.response_class(response=json.dumps({"error_message": "Invalid Value For 'amount_due'"}), status=344,
                                  mimetype='application/json')
    try:
        checking_date = dt.datetime.strptime(request_data['dob'], "%Y-%m-%d")
    except:
        return app.response_class(response=json.dumps({"error_message": "dob expects YYYY-MM-DD format"}), status=344,
                                  mimetype='application/json')
    try:
        with sqlite3.connect(DATABASE, isolation_level='EXCLUSIVE', timeout=10) as connection:
            db = connection.cursor()
            db.execute(
                """INSERT INTO 'student_info' ('first_name','last_name','dob','amount_due') VALUES('{}','{}','{}',{});""".format(
                    request_data['first_name'], request_data['last_name'], request_data['dob'],
                    request_data['amount_due']))
        return app.response_class(response=json.dumps({"message": "New Record Created", "student_id": db.lastrowid}), status=201,
                                  mimetype='application/json')
    except Exception as e:
        return app.response_class(
            response=json.dumps({"error_message": "Error Creating New Record", "execption": str(e)}), status=502,
            mimetype='application/json')


@app.route('/read', methods=["GET", "POST"])
def read_record():
    if request.args.get("student_id") == "*":
        query_condition = ""
    else:
        try:
            query_condition = """ where student_id={}""".format(int(request.args.get("student_id")))
        except TypeError:
            return app.response_class(json.dumps({"error_message": "Student ID not provided"}), status=400,
                                      mimetype='application/json')
        except ValueError:
            return app.response_class(json.dumps({"error_message": "Invalid Student ID"}), status=400,
                                      mimetype='application/json')
    try:
        with sqlite3.connect(DATABASE) as connection:
            connection.row_factory = sqlite3.Row
            db = connection.cursor()
            db.execute("""SELECT * FROM 'student_info'{}""".format(query_condition))
            query_output = db.fetchall()
            if len(query_output) == 0:
                return app.response_class(response=json.dumps({"message": "No Record Found"}), status=200,
                                          mimetype='application/json')
            response = [dict(record) for record in query_output]
        return app.response_class(response=json.dumps({"records": response}), status=200, mimetype='application/json')
    except Exception as e:
        return app.response_class(
            response=json.dumps({"error_message": "Error Retrieving Record", "execption": str(e)}), status=502,
            mimetype='application/json')


@app.route('/update', methods=["PUT", "POST"])
def update_record():
    request_data = dict(request.args)
    try:
        student_id = int(request.args.get("student_id"))
    except TypeError:
        return app.response_class(json.dumps({"error_message": "Student ID not provided"}), status=400, mimetype='application/json')
    except ValueError:
        return app.response_class(json.dumps({"error_message": "Invalid Student ID"}), status=400, mimetype='application/json')

    sql_query = "UPDATE 'student_info' set "
    for key, value in request_data.items():
        if key in list(DATA_SKELETON.keys()):
            if key == "amount_due":
                try:
                    value= float(value)
                except ValueError:
                    return app.response_class(json.dumps({"error_message": "Invalid Value for 'amount_due'"}), status=400, mimetype='application/json')
            sql_query += f"{key} = {value}"

    sql_query += f" where student_id = {student_id}"

    try:
        with sqlite3.connect(DATABASE, isolation_level='EXCLUSIVE', timeout=10) as connection:
            db = connection.cursor()
            db.execute(sql_query)
        return app.response_class(response=json.dumps({"message": f"Student ID {student_id} Record Deleted"}), status=200,
                                  mimetype='application/json')
    except Exception as e:
        return app.response_class(
            response=json.dumps({"error_message": "Error Updating Record", "execption": str(e)}), status=502,
            mimetype='application/json')


@app.route('/delete', methods=["DELETE", "POST"])
def delete_record():
    try:
        student_id = int(request.args.get("student_id"))
    except TypeError:
        return app.response_class(json.dumps({"error_message": "Student ID not provided"}), status=400, mimetype='application/json')
    except ValueError:
        return app.response_class(json.dumps({"error_message": "Invalid Student ID"}), status=400, mimetype='application/json')
    
    try:
        with sqlite3.connect(DATABASE, isolation_level='EXCLUSIVE', timeout=10) as connection:
            db = connection.cursor()
            db.execute(f"DELETE from student_info WHERE student_id = {student_id}")
        return app.response_class(response=json.dumps({"message": f"Student ID {student_id} Record Deleted"}), status=200,
                                  mimetype='application/json')
    except Exception as e:
        return app.response_class(
            response=json.dumps({"error_message": "Error Deleting Record", "execption": str(e)}), status=502,
            mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
