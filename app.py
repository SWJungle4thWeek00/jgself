from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import requests

app = Flask(__name__)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.week00  # 'dbsparta'라는 이름의 db를 만들거나 사용합니다.

@app.route('/')
def main():
    return render_template('upload_content.html')


@app.route('/memo', methods=['POST'])
def post_article():
    # 1. 클라이언트로부터 데이터를 받기
    name = request.form['name_client']  # 클라이언트로부터 url을 받는 부분
    sex = request.form['sex_client']  # 클라이언트로부터 comment를 받는 부분
    mbti = request.form['mbti_client']  # 클라이언트로부터 comment를 받는 부분
    intro = request.form['intro_client']  # 클라이언트로부터 comment를 받는 부분
    git_id = request.form['git_id_client']  # 클라이언트로부터 comment를 받는 부분
    

    content = {
        'name': name, 
        'sex': sex, 
        'mbti': mbti, 
        'intro': intro,
        'git_id': git_id
    }

    # 3. mongoDB에 데이터를 넣기
    db.contents.insert_one(content)

    return jsonify({'result': 'success'})


if __name__=='__main__':    
    app.run('0.0.0.0', port=5000, debug=True)