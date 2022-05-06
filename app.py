from flask import Flask, render_template, request, jsonify, redirect, url_for
import hashlib
import jwt
import datetime


app = Flask(__name__)

SECRET_KEY = '$timeatk1'

# DB 연결 코드
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.timeattack

USER = ()

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.USER.find_one({"id": payload['id']})  # id, num, nickname, feed_images, content, like, reply
        # feed_info = []
        # for follower in user_info['following']:
        #     feed = list(db.FEED.find({'nickname': follower}))  # num, nickname, feed_images, content, like, reply
        #     if feed is not None:
        #         feed_info.extend(feed)
        return render_template('/index.html', users=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("signup"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("signup"))

@app.route('/signup')
def signup():
    return render_template('/signup.html')

@app.route('/logout')
def logout():
    token_receive = request.cookies.get('mytoken')
    if token_receive is not None:
        return jsonify({'msg':'로그아웃 완료!'})



@app.route("/api/join", methods=["POST"])
def api_join():
    id_receive = request.form['id_give']
    pwd_receive = request.form['pwd_give']

    hashed_pw = hashlib.sha256(pwd_receive.encode('utf-8')).hexdigest()

    doc = {
        'id': id_receive,
        'pwd': hashed_pw,
    }
    db.USER.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '회원 가입 완료'})


@app.route("/api/id_dup", methods=["POST"])
def id_dup():
    id_receive = request.form['id_give']
    id_dup = bool(db.USER.find_one({'id': id_receive}))
    return jsonify({'duplicate': id_dup})


@app.route("/api/nick_dup", methods=["POST"])
def nick_dup():
    nick_receive = request.form['nick_give']
    nick_dup = bool(db.USER.find_one({'nickname': nick_receive}))
    return jsonify({'duplicate': nick_dup})


@app.route("/api/login", methods=["POST"])
def api_login():
    id_receive = request.form['id_give']
    pwd_receive = request.form['pwd_give']

    hashed_pw = hashlib.sha256(pwd_receive.encode('utf-8')).hexdigest()

    user = db.USER.find_one({'id': id_receive, 'pwd': hashed_pw})
    print(user)

    if user is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1800)
        }
        print(payload)
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        print(token)
        return jsonify({'result': 'success', 'token': token, 'msg': '로그인 성공'})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})


@app.route('/api/valid', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})

    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)