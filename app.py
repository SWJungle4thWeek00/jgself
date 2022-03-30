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
        if len(list(db.profiles.find({'userId' : userId} ) ) ) != 0:
            db.profiles.delete_one({'userId':userId})    
        
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
    user_row_in_checkEmails = temp_list[0]
    user_row_in_profiles = list(db.profiles.find({'userId': user_row_in_checkEmails['email']}))

    if len(user_row_in_profiles) != 0:
        print('here');
        return render_template(
            'upload.html', 
            user_name = user_row_in_profiles[0]['name'], 
            user_id = session['userId'],
            jinja_sex = user_row_in_profiles[0]['sex'],
            jinja_mbti = user_row_in_profiles[0]['mbti'],
            jinja_intro = user_row_in_profiles[0]['intro'],
            jinja_git_id = user_row_in_profiles[0]['git_id']
        );
    else:
        print(user_row_in_profiles);
        return render_template(
            'upload.html', 
            user_name = user_row_in_checkEmails['name'], 
            user_id = session['userId'],
            jinja_sex = '남자',
            jinja_mbti = 'INTJ',
            jinja_intro = '',
            jinja_git_id = ''
        ); 
        
    

    

@app.route('/comment', methods=['POST'])
def postComment():
    receiver = request.form['receiver_client']
    writer = request.form['writer_client']
    writer_name = list(db.checkEmails.find({'email' : session['userId']}))[0]['name']
    comment = request.form['comment_client']  # 클라이언트로부터 pw를 받는 부분
    

    db.comments.insert_one({'profileId':receiver, 'writer': writer, 'writer_name': writer_name, 'comment':comment})

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
        profiles = list(db.profiles.find({'name' : profileId}))
        emails = profiles[0]['userId']
        comments = list(db.comments.find({'profileId' : emails}))
        count = len(comments)

        img = url_for('static', filename = profiles[0]['mbti']+'.png')
            
        return render_template('detail.html', userId=userId, profiles = profiles[0], comments = comments, 
                                            count=count, receiver = emails, receiver_name = profiles[0]['name'], profiles_row = profiles, imgUrl = img
        )

    else:
        return redirect("/login")



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)