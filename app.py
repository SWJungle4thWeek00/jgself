from operator import ne
from flask import Flask, make_response, render_template, jsonify, request, session, redirect, make_response, url_for
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
#from flask_bcrypt import Bcrypt
import bcrypt

app = Flask(__name__)
app.secret_key = 'jgself'

client = MongoClient('mongodb://test:test@13.209.40.199',27017)  # mongoDB는 27017 포트로 돌아갑니다.
# client = MongoClient('mongodb://test:test@13.209.40.199',27017)
db = client.jgself  # 'dbsparta'라는 이름의 db를 만들거나 사용합니다.

@app.route('/memo', methods=['POST'])
def post_article():
    if 'userId' in session:
        userId = session['userId']
        name = list(db.checkEmails.find({'email':userId}))[0]['name']

        # 1. 클라이언트로부터 데이터를 받기
        # name = request.form['name_client']  # 클라이언트로부터 url을 받는 부분
        sex = request.form['sex_client']  # 클라이언트로부터 comment를 받는 부분
        mbti = request.form['mbti_client']  # 클라이언트로부터 comment를 받는 부분
        intro = request.form['intro_client']  # 클라이언트로부터 comment를 받는 부분
        git_id = request.form['git_id_client']  # 클라이언트로부터 comment를 받는 부분
        
        content = {
            'userId' : userId,
            'name': name, 
            'sex': sex, 
            'mbti': mbti, 
            'intro': intro,
            'git_id': git_id
        }

        # 3. mongoDB에 데이터를 넣기
        db.profiles.insert_one(content)

        return jsonify({'result': 'success'})

    else:
        return redirect("/login")


@app.route('/')
def home():
    if 'userId' in session:
        userId = session['userId']

        profiles = list(db.profiles.find())

        imgFiles = []
        for i in range(len(profiles)):
            img = url_for('static', filename = profiles[i]['mbti']+'.png')
            imgFiles.append(img)

        return render_template('index.html', userId=userId, profiles = profiles, imgFiles = imgFiles)
    else:
        return redirect("/login")


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    if request.method == 'POST':
        # 1. 클라이언트로부터 데이터를 받기
        params = request.get_json()
        id_receive = params['id_give']
        pw_receive = params['pw_give']  # 클라이언트로부터 pw를 받는 부분

        encoded_new_password = pw_receive.encode('utf-8')

        check = list(db.users.find({'userId' : id_receive}))

        if len(check) > 0:
    
            if(bcrypt.checkpw(encoded_new_password, check[0]['password'])):
                resp = make_response("Login 완료!")
                resp.set_cookie('userId',id_receive)
                session['userId'] = id_receive
                
                return jsonify({'result': 'success'})
            else:
                return jsonify({'result': 'false'})
        else:
            print("id 없음!")
            return jsonify({'result': 'false'})

    else:
        return render_template("login.html")

@app.route('/comment', methods=['POST'])
def postComment():
    # 1. 클라이언트로부터 데이터를 받기
    params = request.get_json()
    id_receive = params['id_give']
    pw_receive = params['pw_give']  # 클라이언트로부터 pw를 받는 부분

    encoded_password = pw_receive.encode('utf-8')
    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())

    db.users.insert_one({'userId':id_receive,'password': hashed_password})

    return jsonify({'result': 'success'})


@app.route('/idCheck', methods=['POST'])
def read_userId():
    params = request.get_json()
    id_receive = params['id_give']
    result = list(db.users.find( {'userId': id_receive}))
    emailCheck = list(db.checkEmails.find({'email' : id_receive}))

    if len(result) > 0 or len(emailCheck) < 1:
        return jsonify({'result': 'false'})
    else:
        return jsonify({'result': 'success'})

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userId', None)
    return redirect('/')

@app.route('/upload', methods=['GET'])
def getUpload():
    
    # userName = db.checkEmails.find_one({'email' : session['userId']},{'name' : True})
    temp_list = list(db.checkEmails.find({'email':session['userId']}))
    return render_template('upload.html', user_name = temp_list[0]['name'], user_id = session['userId'])



@app.route('/comment/doyoung', methods=['POST'])
def getPostComments():
    # 1. 클라이언트로부터 데이터를 받기
    params = request.get_json()
    receiver_client = params['receiver']
    writer_client = params['writer']
    comment_client = params['comment']  # 클라이언트로부터 pw를 받는 부분

    db.comments.insert_one({'receiver':receiver_client,'writer': writer_client, 'comment':comment_client})

    return jsonify({'result': 'success'})


@app.route('/signup', methods=['POST', 'GET'])
def signUp_user():
    if request.method == 'POST':
        # 1. 클라이언트로부터 데이터를 받기
        params = request.get_json()
        id_receive = params['id_give']
        pw_receive = params['pw_give']  # 클라이언트로부터 pw를 받는 부분

        encoded_password = pw_receive.encode('utf-8')
        hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
        
        db.users.insert_one({'userId':id_receive,'password': hashed_password})

        return jsonify({'result': 'success'})

    else:
        return render_template("signup.html")

  
@app.route('/profile-detail', methods=['GET'])
def profileDetail():
    if 'userId' in session:
        userId = session['userId']
        profileId = request.args.get("profileId")

        profiles = list(db.profiles.find({'userId' : profileId}))
        comments = list(db.comments.find({'profileId' : profileId}))
        return render_template('detail.html', userId=userId, profiles = profiles, comments = comments)
    else:
        return redirect("/login")



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)