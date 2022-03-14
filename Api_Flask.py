from ast import arg
from flask import Flask, jsonify, request, json, Response,render_template
from flask_restful import reqparse
from pymongo import MongoClient
import logging as log


class MongoAPI:
    def __init__(self, data):
        self.client = MongoClient("mongodb://localhost:27017/")  
      
        database = data['database']
        collection = data['collection']
        cursor = self.client[database]
        self.collection = cursor[collection]
        self.data = data


    def read(self):
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output
    
    def all_title(self):
        documents_title = self.collection.find({},{"Titre":1,"_id":0})
        output = [{item: data[item] for item in data if item != '_id'} for data in documents_title]
        return output
    
    def search_by_title(self,data):
        filt = data['Title']["Titre"]
        response = self.collection.find({"Titre": filt})
        output = [{item: data[item] for item in data if item != '_id'} for data in response]
        return {'results' : output}        

    def write(self, data):
        log.info('Writing Data')
        new_document = data['Document']
        response = self.collection.insert_one(new_document)
        output = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response.inserted_id)}
        return output

    def update(self):
        filt = self.data['Filter']
        updated_data = {"$set": self.data['DataToBeUpdated']}
        response = self.collection.update_one(filt, updated_data)
        output = {'Status': 'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
        return output


    def delete(self, data):
        filt = data['Filter']
        response = self.collection.delete_one(filt)
        output = {'Status': 'Successfully Deleted' if response.deleted_count > 0 else "Document not found."}
        return output


app = Flask(__name__)

@app.route('/')
def base():
    return Response(response=json.dumps({"Status": "UP"}),
                    status=200,
                    mimetype='application/json')


@app.route('/shows_datas', methods=['GET'])
def mongo_read():
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('collection', type=str, required=True)
    parser.add_argument('database', type=str, required=True)
    args = parser.parse_args()
    data2 = {"database":str(args["database"]),"collection":str(args["collection"])}


    
    data = request.json
    if args["database"] is None or args["collection"] is None:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data2)
    response = obj1.read()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route('/all_titles', methods=['GET'])
def mongo_read_titles():
    data = request.json
    if data is None or data == {}:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.all_title()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route('/find_by_title', methods=['GET']) ###§!à revoir!§
def mongo_find_by_title():
    data = request.json
    if data is None or data == {} or 'Title' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.search_by_title(data)
    return response
    # return Response(response=json.dumps(response),
    #                 status=200,
    #                 mimetype='application/json')

@app.route('/new_movie', methods=['POST'])
def mongo_write():
    data = request.json
    if data is None or data == {} or 'Document' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.write(data)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')


@app.route('/uptade_movie', methods=['PUT'])
def mongo_update():
    data = request.json
    if data is None or data == {} or 'DataToBeUpdated' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.update()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')


@app.route('/delete_movie', methods=['DELETE'])
def mongo_delete():
    data = request.json
    if data is None or data == {} or 'Filter' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.delete(data)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

  


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')


    





