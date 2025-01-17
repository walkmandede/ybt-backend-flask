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
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

## init mongodb
mongo = PyMongo(app)


#init functions

def register_bps():
    from application.blueprints.admin_auth import admin_auth_bp
    app.register_blueprint(admin_auth_bp, url_prefix="/api")

    from application.blueprints.bus_stop import bus_stop_bp
    app.register_blueprint(bus_stop_bp, url_prefix="/api")

def init_api_docs():
    api = Api(app)
    api.namespace('Data', description='Data operations')



if __name__ == '__main__':
    register_bps()
    # init_api_docs()

    print("+++++++++++++")
    print("Started")
    print("+++++++++++++")

    app.run(debug=True,port=2345)
    print("Started")




