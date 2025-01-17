from bson import ObjectId
from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from application.schemas.auth_schema import AdminProfileSchema, LoginSchema
from application.utils.jwt_service import generate_admin_token, validate_admin_token
from application.utils.mongo_collections import MongoCollections
from application.utils.app_util import AppUtils
from application.utils.response_util import create_response

admin_auth_bp = Blueprint('admin-auth', __name__)

# Helper to get MongoDB collections
def get_collections():
    col_admins = MongoCollections.get_collection_instance(MongoCollections.ADMIN_PROFILES)
    col_bus_stops = MongoCollections.get_collection_instance(MongoCollections.BUS_STOPS)
    col_bus_lines = MongoCollections.get_collection_instance(MongoCollections.BUS_LINES)
    return col_admins, col_bus_stops, col_bus_lines


@admin_auth_bp.route('/admin-auth/register', methods=['POST'])
def register():
    """Register a new admin profile."""
    request_data = request.json
    schema = AdminProfileSchema()

    # Validate request data
    validation_errors = AppUtils.validate_schema(schema, request_data)
    if validation_errors:
        return create_response(
            message="Validation errors",
            status_code=400,
            error=validation_errors,
            success=False
        )

    col_admins, col_bus_stops, col_bus_lines = get_collections()
    email = request_data.get("email")
    password = request_data.get("password")
    bus_line_data = request_data.get("busLine")

    # Check if email already exists
    if col_admins.find_one({"email": email}):
        return create_response(
            message="Email already exists.",
            status_code=400,
            success=False
        )

    # Validate bus stops
    bus_stops = bus_line_data.get("busStops")
    existing_stops = list(col_bus_stops.find({"id": {"$in": bus_stops}}, {"id": 1}))
    existing_stop_ids = [stop["id"] for stop in existing_stops]

    if set(bus_stops) != set(existing_stop_ids):
        return create_response(
            message="Invalid or duplicate bus stops.",
            status_code=400,
            success=False
        )

    # Create bus line
    bus_line = {
        "busLineName": bus_line_data["busLineName"],
        "busStops": bus_stops,
        "firstOne": bus_line_data["firstOne"],
        "lastOne": bus_line_data["lastOne"],
    }
    bus_line_id = col_bus_lines.insert_one(bus_line).inserted_id

    # Register admin
    new_admin = {
        "email": email,
        "password": generate_password_hash(password),
        "name": request_data.get("name", ""),
        "role": request_data.get("role", "admin"),
        "busLinesId": str(bus_line_id),
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
    }
    col_admins.insert_one(new_admin)

    return create_response(
        message="Registration successful.",
        status_code=201,
        success=True
    )


@admin_auth_bp.route('/admin-auth/login', methods=['POST'])
def login():
    """Login an admin profile."""
    request_data = request.json
    schema = LoginSchema()

    # Validate request data
    validation_errors = AppUtils.validate_schema(schema, request_data)
    if validation_errors:
        return create_response(
            message="Validation errors",
            status_code=400,
            error=validation_errors,
            success=False
        )

    col_admins, _, _ = get_collections()
    email = request_data.get("email")
    password = request_data.get("password")

    # Find admin by email
    admin = col_admins.find_one({"email": email})
    if not admin or not check_password_hash(admin["password"], password):
        return create_response(
            message="Invalid email or password.",
            status_code=401,
            success=False
        )
    
    token = generate_admin_token(admin["_id"])

    # Return admin profile data with ID
    return create_response(
        message="Login successful.",
        status_code=200,
        data={
            "token" : token
        },
        success=True
    )


@admin_auth_bp.route('/admin-auth/profile', methods=['GET'])
def get_admin_profile():
    """Fetch admin profile using Bearer Token."""
    # Validate Bearer Token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return create_response(
            message="Missing or invalid Authorization header.",
            status_code=401,
            success=False
        )
    token = auth_header.split(" ")[1]  # Extract the token from the header
    admin_id_from_token = validate_admin_token(token)
    if isinstance(admin_id_from_token, str) and "Token" in admin_id_from_token:
        return create_response(
            message=admin_id_from_token,  # Token expired or invalid message
            status_code=401,
            success=False
        )

    # Fetch admin profile from the database
    col_admins, col_bus_stops, col_bus_lines = get_collections()
    admin = col_admins.find_one({"_id": ObjectId(admin_id_from_token)})

    if not admin:
        return create_response(
            message="Admin profile not found.",
            status_code=404,
            success=False
        )

    # Fetch associated bus line details (if applicable)
    bus_line = None
    if admin.get("busLinesId"):
        bus_line = col_bus_lines.find_one({"_id": ObjectId(admin["busLinesId"])}, {"_id": 0})
        bus_line["id"] = admin["busLinesId"]
        if bus_line and "busStops" in bus_line:
            # Fetch full details of each bus stop
            bus_stop_ids = bus_line["busStops"]
            bus_stops = list(col_bus_stops.find({"id": {"$in": bus_stop_ids}}))
            for stop in bus_stops:
                stop["_id"] = str(stop["_id"])  # Convert ObjectId to string
            bus_line["busStops"] = bus_stops

    # Prepare response data
    admin_data = {
        "id": str(admin["_id"]),
        "name": admin["name"],
        "email": admin["email"],
        "role": admin["role"],
        "createdAt": admin["createdAt"],
        "updatedAt": admin["updatedAt"],
        "busLine": bus_line if bus_line else "No associated bus line.",
    }

    return create_response(
        data=admin_data,
        message="Admin profile fetched successfully.",
        status_code=200,
        success=True
    )


# @admin_auth_bp.route('/admin-auth/profile/<string:admin_id>', methods=['GET'])
# def get_admin_profile(admin_id):
#     col_admins, col_bus_stops, col_bus_lines = get_collections()

#     # Validate ObjectId format
#     if not ObjectId.is_valid(admin_id):
#         return create_response(
#             message="Invalid admin ID format.",
#             status_code=400,
#             success=False
#         )

#     # Fetch admin profile
#     admin = col_admins.find_one({"_id": ObjectId(admin_id)})
#     if not admin:
#         return create_response(
#             message="Admin profile not found.",
#             status_code=404,
#             success=False
#         )

#     # Fetch associated bus line details (if applicable)
#     bus_line = None
#     if admin.get("busLinesId"):
#         bus_line = col_bus_lines.find_one({"_id": ObjectId(admin["busLinesId"])}, {"_id": 0})
#         bus_line["id"] = admin["busLinesId"]
#         if bus_line and "busStops" in bus_line:
#             # Fetch full details of each bus stop
#             bus_stop_ids = bus_line["busStops"]
#             bus_stops = list(col_bus_stops.find({"id": {"$in": bus_stop_ids}}))
#             for stop in bus_stops:
#                 stop["_id"] = str(stop["_id"])  # Convert ObjectId to string
#             bus_line["busStops"] = bus_stops

#     # Prepare response data
#     admin_data = {
#         "id": str(admin["_id"]),
#         "name": admin["name"],
#         "email": admin["email"],
#         "role": admin["role"],
#         "createdAt": admin["createdAt"],
#         "updatedAt": admin["updatedAt"],
#         "busLine": bus_line if bus_line else "No associated bus line.",
#     }

#     return create_response(
#         data=admin_data,
#         message="Admin profile fetched successfully.",
#         status_code=200,
#         success=True
#     )
