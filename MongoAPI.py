from flask import Flask, request, json, Response
from pymongo import MongoClient
import logging as log

app = Flask(__name__)


class MongoAPI:
    def __init__(self, data):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s:\n%(message)s\n')
        # self.client = MongoClient("mongodb://localhost:27017/")  # When only Mongo DB is running on Docker.
        self.client = MongoClient("mongodb://mymongo_1:27017/")     # When both Mongo and This application is running on
                                                                    # Docker and we are using Docker Compose

        database = data['database']
        collection = data['collection']
        cursor = self.client[database]
        self.collection = cursor[collection]
        self.data = data

    def check_existance(self, data):
        log.info('Reading All Data')
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        log.info('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

        req_document = data['Document']
        for item in output:
            if 'id' in req_document and 'id' in item:
                    if item['id'] == req_document['id']:
                        return item

        return "Doesn't Exist"

    def write(self, data):
        log.info('Writing Data')
        new_document = data['Document']
        response = self.collection.insert_one(new_document)
        output = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response.inserted_id)}
        return output


@app.route('/')
def base():
    return Response(response=json.dumps({'Status': 'UP'}),
                    status=200,
                    mimetype='application/json')

@app.route('/mongodb', methods=['GET'])
def mongo_check_existance():
    data = request.json
    if data is None or data == {}:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.check_existance(data)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route('/mongodb', methods=['POST'])
def mongo_write():
    data = request.json
    if data is None or data == {} or 'Document' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    exists = obj1.check_existance(data)
    if exists != "Doesn't Exist":
        return exists

    response = obj1.write(data)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

# if __name__ == '__main__':
#     data = {
#         "database": "db_name",
#         "collection": "products",
#     }
#     mongo_obj = MongoAPI(data)
#     print(json.dumps(mongo_obj.read(), indent=4))

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')