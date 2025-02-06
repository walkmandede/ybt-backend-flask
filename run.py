from flask import Flask
import os
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_restx import Api, Resource

#initializing app
app = Flask(__name__)
CORS(app)

# entry route
@app.route('/')
def home():
    return "Welcome to my app! Yangon Bus Tracking System"

app.config.from_object('config.Config')
# app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["MONGO_URI"] = "mongodb+srv://walkmandede:kokolusoepotato@uosbuc.c0oppu4.mongodb.net/yangon_bus_tracking_system"

## init mongodb
mongo = PyMongo(app)


#init functions

def register_bps():
    ## bus stops
    from application.blueprints.bus_stop import bus_stop_bp
    app.register_blueprint(bus_stop_bp, url_prefix="/api")
    ## bus line
    from application.blueprints.bus_line import bus_line_bp
    app.register_blueprint(bus_line_bp, url_prefix="/api")
    ## bus driver
    from application.blueprints.bus_driver import bus_driver_bp
    app.register_blueprint(bus_driver_bp, url_prefix="/api")
    ## bus vehicle
    from application.blueprints.bus_vehicle import bus_vehicle_bp
    app.register_blueprint(bus_vehicle_bp, url_prefix="/api")
    ## users
    from application.blueprints.users.users import user_bp
    app.register_blueprint(user_bp, url_prefix="/api")

def init_api_docs():
    api = Api(app)
    api.namespace('Data', description='Data operations')



if __name__ == '__main__':
    register_bps()
    # init_api_docs()

    print("+++++++++++++")
    print("Started")
    print("+++++++++++++")

    # app.run(debug=True,port=2345)
    app.run(debug=True, host='0.0.0.0', port=2345)
    print("Started")




