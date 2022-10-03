from flask import Flask, request, jsonify, make_response
import sqlite3
from preprocess import textprep
from flask_swagger_ui import get_swaggerui_blueprint
import pandas as pd


# Init app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  #Agar Return JSON dalam urutan yang benar


# flask swagger configs
SWAGGER_URL = '/swaggers'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Tworst!"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


@app.route('/text-clean', methods = ['POST'])
def text_cleaning():
    text = request.form('text')
    json_response = {
        'status code': 200,
        'description': 'API text cleaning',
        'data': (text),
    }
    response_data = jsonify(json_response)
    return response_data


if __name__ == '__main__':
    app.run(debug=True)