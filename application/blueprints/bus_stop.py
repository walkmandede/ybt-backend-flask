from bson import ObjectId
from flask import Blueprint, request
from application.schemas.bus_stop_schema import BusStopSchema
from application.utils.app_util import AppUtils
from application.utils.mongo_collections import MongoCollections
from application.utils.response_util import create_response

# Blueprint for bus stop operations
bus_stop_bp = Blueprint('bus-stop', __name__)

@bus_stop_bp.route('/bus-stop', methods=['POST'])
def create_bus_stop():
    data = request.json
    if not data:
        return create_response(
            data=None,
            success=False,
            status_code=400,
            message="No data provided!"
        )
    
    # Validation
    result = AppUtils.validate_schema(BusStopSchema(), data)
    if result is not None:
        return create_response(
            data=str(result),
            success=False,
            status_code=400,
            message="Validation Error"
        )
    
    # Save the document to the MongoDB collection
    try:
        col = MongoCollections.get_collection_instance(MongoCollections.BUS_STOPS)
        col.insert_one(data)
        return create_response(
            data=None,
            success=True,
            status_code=201,
            message="Bus stop created successfully!"
        )
    except Exception as e:
        return create_response(
            data=None,
            success=False,
            status_code=500,
            message=str(e)
        )

@bus_stop_bp.route('/bus-stop', methods=['GET'])
def fetch_bus_stops():
    try:
        documents = MongoCollections.get_collection_instance(MongoCollections.BUS_STOPS).find()
        result = []
        for doc in documents:
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
            result.append(doc)
        
        return create_response(
            success=True,
            status_code=200,
            data=result,
            message="Bus stops fetched successfully!"
        )
    except Exception as e:
        return create_response(
            data=None,
            success=False,
            status_code=500,
            message=str(e)
        )

@bus_stop_bp.route('/bus-stop/<bus_stop_id>', methods=['GET'])
def fetch_bus_stop_by_id(bus_stop_id):
    try:
        col = MongoCollections.get_collection_instance(MongoCollections.BUS_STOP)
        document = col.find_one({"_id": ObjectId(bus_stop_id)})
        if not document:
            return create_response(
                data=None,
                success=False,
                status_code=404,
                message="Bus stop not found!"
            )
        document["_id"] = str(document["_id"])
        return create_response(
            data=document,
            success=True,
            status_code=200,
            message="Bus stop fetched successfully!"
        )
    except Exception as e:
        return create_response(
            data=None,
            success=False,
            status_code=500,
            message=str(e)
        )

@bus_stop_bp.route('/bus-stop/<bus_stop_id>', methods=['PUT'])
def update_bus_stop(bus_stop_id):
    data = request.json
    if not data:
        return create_response(
            data=None,
            success=False,
            status_code=400,
            message="No data provided!"
        )
    
    # Validation
    result = AppUtils.validate_schema(BusStopSchema(), data)
    if result is not None:
        return create_response(
            data=str(result),
            success=False,
            status_code=400,
            message="Validation Error"
        )
    
    # Update document
    try:
        col = MongoCollections.get_collection_instance(MongoCollections.BUS_STOP)
        db_result = col.update_one(
            {"_id": ObjectId(bus_stop_id)},
            {"$set": data}
        )
        if db_result.modified_count == 0:
            return create_response(
                data=None,
                success=False,
                status_code=404,
                message="Bus stop not found!"
            )
        return create_response(
            data=None,
            success=True,
            status_code=200,
            message="Bus stop updated successfully!"
        )
    except Exception as e:
        return create_response(
            data=None,
            success=False,
            status_code=500,
            message=str(e)
        )

@bus_stop_bp.route('/bus-stop/<bus_stop_id>', methods=['DELETE'])
def delete_bus_stop(bus_stop_id):
    try:
        col = MongoCollections.get_collection_instance(MongoCollections.BUS_STOP)
        result = col.delete_one({"_id": ObjectId(bus_stop_id)})
        if result.deleted_count == 0:
            return create_response(
                data=None,
                success=False,
                status_code=404,
                message="Bus stop not found!"
            )
        return create_response(
            data=None,
            success=True,
            status_code=200,
            message="Bus stop deleted successfully!"
        )
    except Exception as e:
        return create_response(
            data=None,
            success=False,
            status_code=500,
            message=str(e)
        )
