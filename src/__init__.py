from flask import Flask, session




def create_app(config_name= 'default'):
    app = Flask(__name__)
    from src.config.config import config
    app.config.from_object(config[config_name])
    return app 