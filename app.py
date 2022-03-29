from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

app = Flask(__name__)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbsparta  # 'dbsparta'라는 이름의 db를 만들거나 사용합니다.

@app.route('/')
def home():
    return render_template('index.html')

# 생성


@app.route('/memo', methods=['POST'])
def post_memo():
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    memo = {'title': title_receive, 'content': content_receive}

    db.memo.insert_one(memo)

    return jsonify({'result': 'success'})


# 삭제
@app.route('/memo/delete', methods=['POST'])
def delete_memo():
    _id_receive = request.form['_id_give']
    db.memo.delete_one({'_id': ObjectId(_id_receive)})
    return jsonify({'result': 'success'})

# 수정


@app.route('/memo/revise', methods=['POST'])
def rivse_memo():
    memos = []
    result = list(db.memo.find({}))
    for memo in result:
        memo['_id'] = str(memo['_id'])
        memos.append(memo)
    _id_receive = request.form['_id_give']
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    db.memo.update_one({'_id': ObjectId(_id_receive)}, {
                       '$set': {'title': title_receive}})

    db.memo.update_one({'_id': ObjectId(_id_receive)}, {
                       '$set': {'content': content_receive}})
    return jsonify({'result': 'success'})


@app.route('/memo/read', methods=['GET'])
def read_memo():
    memos = []
    result = list(db.memo.find({}))
    for memo in result:
        memo['_id'] = str(memo['_id'])
        memos.append(memo)
    return jsonify({'result': 'success', 'memo': result})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)