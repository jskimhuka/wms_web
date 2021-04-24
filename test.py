import codecs
import time
import pymysql
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_url = "mysql+pymysql://root:1234@localhost/brc_wms"
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
db = SQLAlchemy(app)  # DB Alchemy 합체함

app.secret_key = 'secret_key'  # 세션 생성시 반드시 시크릿키 만들자 (php 랑 틀리네)


# db.init_app(app)

# SQLALCHEMY_TRACK_MODIFICATIONS = False  뒤에 있던 오류 제거 SQLAlchemy

class comp(db.Model):
    __tablename__ = 'co_info'
    co_code = db.Column(db.Integer, primary_key=True, autoincrement=True)
    co_name = db.Column(db.String(45))


# SQLALCHEMY_TRACK_MODIFICATIONS = False

class Weinfo(db.Model):
    __tablename__ = 'we_info'
    no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    co_code = db.Column(db.Integer, ForeignKey('co_info.co_code'))
    w_code = db.Column(db.Integer, primary_key=True)
    w_name = db.Column(db.String())


@app.route("/")
def hello():
    session['s_login'] = False
    session['sessionOK'] = False

    return render_template("wms_login.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    ip_name = request.form["co_name"]
    ip_id = request.form["co_id"]
    ip_pw = request.form["co_pw"]

    connection = getconnection()

    sql = "SELECT co_code FROM co_info WHERE co_name= %s "
    cursor = connection.cursor()
    cursor.execute(sql, ip_name)
    co_com = cursor.fetchone()
    connection.commit()
    session['sco_code'] = str(co_com[0]).zfill(4)
    session['sco_id'] = ip_id
    ip_cd = session['sco_code']
    connection = getconnection()

    # sql2 = "SELECT CAST(AES_DECRYPT(UNHEX(PASS), SHA2('My secret passphrase',512)) as char)
    # FROM user_info WHERE ID= %s " ## 복호화코드
    # sql2 = "INSERT INTO user_info VALUES
    # (%s, %s, HEX(AES_ENCRYPT(%s,SHA2('My secret passphrase',512))))"

    sql2 = "SELECT HEX(AES_ENCRYPT(%s,SHA2('My secret passphrase',512))) from user_info " \
           "where ID = %s"
    cursor = connection.cursor()
    cursor.execute(sql2, (ip_pw, ip_id))
    pass_re = cursor.fetchone()
    connection.commit()
    session['pass_ok'] = pass_re[0]

    sql = "SELECT count(ID) FROM user_info WHERE co_code= %s and ID = %s and PASS = %s "
    cursor = connection.cursor()
    cursor.execute(sql, (ip_cd, ip_id, session['pass_ok']))
    logok = cursor.fetchone()
    connection.commit()
    loginok = logok[0]

    if loginok == 1:
        session['sco_id'] = ip_id
        session['sco_name'] = ip_name
        session['s_login'] = True
        return test01()
    else:
        return render_template("login_x.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if session['s_login']:
        session['s_login'] = False
        session.clear
        session['sessionOK'] = True
        ok = session['sessionOK']
        return render_template("wms_login.html", OK=ok)
    else:
        ok = False
        return render_template("wms_login.html", OK=ok)


@app.route("/popup", methods=["GET", "POST"])
def popup():
    session['popOK'] = False

    if not session['popOK']:
        return render_template("popup.html")
    else:
        return render_template("main.html")


@app.route("/popup_ok", methods=["GET", "POST"])
def popup_ok():
    pop_id = request.form["pop_id"]
    pop_pwd = request.form["pop_pwd"]

    connection = getconnection()

    sql = "SELECT count(co_code) FROM user_info WHERE ID= %s "
    cursor = connection.cursor()
    cursor.execute(sql, pop_id)
    id_count = cursor.fetchone()
    connection.commit()

    if id_count[0] == 0:
        sql2 = "INSERT INTO user_info VALUES (%s, %s, HEX(AES_ENCRYPT(%s,SHA2('My secret passphrase',512))))"
        cursor = connection.cursor()
        cursor.execute(sql2, (session['sco_code'], pop_id, pop_pwd))
        popup_re = cursor.fetchone()
        connection.commit()

        return render_template("popup_o.html", popup_re=popup_re)
    else:
        return render_template("popup_x.html")


def getconnection():
    return pymysql.connect(
        host="localhost",
        db="BRC_WMS",
        user="root",
        password="1234",
        charset="utf8"
        # cursorclass = pymysql.cursors.DictCursor
    )


@app.route("/test", methods=["GET", "POST"])
def test01():
    players = comp.query.all()
    # players = comp.query.limit(2).all()
    # players = comp.query.filter(player.no >=2).all()

    # stringToInt = ord('a')
    # intToString = chr(stringToInt)

    # print(stringToInt)
    # print(intToString)
    file_t = codecs.open("test_t.txt", "r", "utf-8")
    line_t = file_t.readlines()
    file_t.close()
    test01 = "test!!!!!!!!!"

    # wco_name = request.form["wco_name"]
    # wco_user = request.form["wco_user"]
    # wpa_code = request.form["wpa_code"]

    return render_template("main.html", test01=test01,
                           line_t=line_t, players=players)


@app.route("/ADD_S", methods=["POST"])
def ADD():
    p_code = request.form["p_code"]
    n_code = request.form["n_code"]
    w_code = request.form["w_code"]

    file = codecs.open("test_t.txt", "a", "utf-8")
    file.write(p_code + "," + n_code + "," + w_code + ","
               + time.strftime('%y-%m-%d // ' + '%H' + ':' + '%M' + ':' + '%S') + "\n")
    file.close()

    return render_template("ADD_S.html",
                           p_code=p_code, n_code=n_code, w_code=w_code)


@app.route("/show/<int:id>")
def show_info(id):
    # connection = getConnection()
    # message="詳細情報"+str(id)

    # sql = "SELECT * FROM tb1 where tb1.no = %c"
    # cursor = connection.cursor()
    # cursor.execute(sql, id)
    # players = cursor.fetchone()
    # connection.close()

    s_info = comp.query.get(id)

    return render_template("show_info.html", s_info=s_info)


@app.route("/we", methods=["POST"])
def we_info():
    we_name = request.form["we_name"]

    connection = getconnection()

    sql = "SELECT count(co_code)+1 FROM WE_info where co_code = %s"
    cursor = connection.cursor()
    cursor.execute(sql, session['sco_code'])
    we_count = cursor.fetchone()
    connection.commit()

    sco_code = int(session['sco_code'])
    ware_code = we_count[0]
    ware_code2 = chr(sco_code + 64) + "-" + str(we_count[0]).zfill(2)

    sql2 = "INSERT INTO WE_info VALUES (%s , %s , %s, %s)"
    cursor = connection.cursor()
    cursor.execute(sql2, (sco_code, ware_code, ware_code2, we_name))
    we_cre = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()

    # we_count = Weinfo.query.filter_by(w_name="ware-01").all()
    # we_count = Weinfo.query.all()

    # we = weinfo.select()
    # we_count = db.execute(we)
    # s_info = comp.query.get(id)

    return render_template("WE_info.html", we_count=we_count,
                           sco_code=sco_code, ware_code=ware_code,
                           ware_code2=ware_code2, we_name=we_name)
