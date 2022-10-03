# Importing Libraries
import sqlite3
from flask import Flask, jsonify, request
from flasgger import Swagger, LazyString, LazyJSONEncoder 
from flasgger import swag_from
import re

#Flask and Swagger Initialization 
app = Flask(__name__)

#import libraries 
import pandas as pd 


#TEXT CLEANING
#Mengganti seluruh karakter menjadi lowercase 
def lowerchar(text): 
    return text.lower()

#Menghilangkan seluruh karakter non-alphanumerik 
def rmv_nonalphanumeric(text):
    text = re.sub('[^0-9A-Za-z]+',' ',text)
    return text

#Menghilangkan karakter yang tidak diperlukan 
def rmv_unnchar(text): 
    text = re.sub('\n',' ',text) #menghilangkan enter pada teks 
    text = re.sub('rt',' ',text) #menghilangkan simbol retweet pada twitter
    text = re.sub('user',' ',text) #menghilangkan karakter username 
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text)
    text = re.sub('  +',' ',text) #menghilangkan kelebihan spasi
    return text

#import dictionary alay untuk mapping kata2 tidak baku  
alay_dict = pd.read_csv('new_kamusalay.csv', encoding='latin-1', header=None)
#rename kolum pada dictionary 
alay_dict = alay_dict.rename(columns={0:'original',
                                    1:'replacement'})

#mengubah kata-kata yang tidak baku pada teks 
alay_dict_map = dict(zip(alay_dict['original'], alay_dict['replacement']))
def baku(text):
    return ' '.join([alay_dict_map[word] if word in alay_dict_map else word for word in text.split(' ')])

#Gabungan fungsi 
def textprep(text):
    text = lowerchar(text)
    text = baku(text)
    text = rmv_nonalphanumeric(text)
    text = rmv_unnchar(text)
    return text

#INISIALISASI DATABASE
db = sqlite3.connect('storage.db',check_same_thread=False)
db.row_factory = sqlite3.Row
c = db.cursor()
c.execute("create table if not exists databases (id INTEGER PRIMARY KEY AUTOINCREMENT, original TEXT, cleansed TEXT);")
db.commit() 

    
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda:'API Documentation for Data Processing and Modeling'),
    'version': LazyString(lambda:'1.0.0'),
    'description': LazyString(lambda:'Dokumentasi API untuk Data Processing dan Modeling'),
    }, 
    host = LazyString(lambda: request.host)    
)
swagger_config = {
    "headers": [],
    "specs":[
        {
            "endpoint":'docs',
            "route":'/docs.json',
        }
    ],
    "static_url_path":"/flasgger_static",
    "swagger_ui": True,
    "specs_route":"/docs"
}
swagger = Swagger(app,template=swagger_template, 
                config=swagger_config)


#HOMEPAGE
@swag_from("docs/hello.yml", methods = ['GET'])
@app.route('/', methods = ['GET'])
def hello_world(): 
    json_response = {
        'status code': 200,
        'description' : 'Home',
        'data': 'Tweet and Word Cleaning',
    }
    response_data = jsonify(json_response)
    return response_data

#CHECKING DATABASES
@swag_from("docs/check_db.yml", methods = ['GET'])
@app.route("/databases", methods = ['GET'])
def database_check():
    query = "select * from databases"
    select_tweet = c.execute(query)
    tweet = [
        dict(id=row[0], original=row[1], cleansed=row[2])
        for row in select_tweet.fetchall()
    ]
    

    json_response = {
        'status code': 200,
        'description' : 'Checking Database',
        'data': tweet,
    }
    response_data = jsonify(json_response)
    return response_data

#INPUT TEXT
@swag_from("docs/text_process.yml", methods = ['POST'])
@app.route('/text-clean', methods = ['POST'])
def text_cleaning():
    text = request.form.get("text")
    cleansed = textprep(text)
    query = "insert into databases (original,cleansed) values (? , ?)"
    values = (text,cleansed)
    c.execute(query,values)
    db.commit()

    json_response = {
        'status code': 200,
        'description': 'Text Cleaning',
        'data': cleansed,
    }
    response_data = jsonify(json_response)
    return response_data

#INPUT CSV
@swag_from("docs/input_csv.yml",methods=['POST'])
@app.route("/csv-clean", methods=['POST'])
def csv_cleaning():
    file = request.files["file"]
    try:
        df = pd.read_csv(file, encoding='iso-8859-1')
    except:
        df = pd.read_csv(file, encoding='utf-8')
    col_1 = df.iloc[:,0]
    for text in col_1:
        bersih = textprep(text)
        query = "insert into databases (original,cleansed) values(?,?)"
        values = (text, bersih)
        c.execute(query, values)
        db.commit()
    json_response = {
        'status code': 200,
        'description': 'CSV Upload and Processing',
        'data': 'File successfully uploaded',
    }
    response_data = jsonify(json_response)
    return response_data
    
#Cleaning Databases Data
@swag_from("docs/delete.yml",methods=['DELETE'])
@app.route("/delete_data", methods=['DELETE'])
def put_data():
    c.execute("DELETE FROM databases;")
    c.execute("delete from sqlite_sequence where name='databases';")
    db.commit()

    json_response = {
        'status code': 200,
        'description': 'Cleaning Databases Record',
        'data': 'Table Cleansed',
    }
    response_data = jsonify(json_response)
    return response_data


if __name__ == '__main__':
    app.run()    