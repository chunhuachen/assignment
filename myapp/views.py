import json
import time
import jwt
import datetime
import sqlalchemy, sqlalchemy.orm
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from sqlalchemy import create_engine
from myapp.models import Users, Base
from rest_framework import exceptions

engine = create_engine("postgresql://ui_test:1234@db:5432/ui_test")
Base.metadata.create_all(engine)

def index(request):
    return HttpResponse("Hello, world. You're at the myapp index.\r\n")

def test(request):
    return HttpResponse("test!\r\n")

def gen_token(user):
    value = {
        "account": user.acct,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=5),
    }
    encoded_jwt = jwt.encode(value, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt.decode("utf-8")

def verify_token(request):
    authorization_header = request.headers.get("Authorization")
    if authorization_header:
        try:
            access_token = authorization_header.split(" ")[1]
            decoded = jwt.decode(access_token.encode("utf-8"), settings.SECRET_KEY, algorithm="HS256")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("access_token expired")
        except IndexError:
            raise exceptions.AuthenticationFailed("Token prefix missing")

        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        session = Session()

        if "account" in decoded:
            user = session.query(Users).filter_by(acct=decoded["account"]).first()
        else:
            raise exceptions.AuthenticationFailed("User not found")
        return True
    return False
    

@csrf_exempt
def user_login(request):
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()

    result = ""
    msg = ""
    resp = {}
    d = json.loads(request.body)
    if "user" in d and "pwd" in d:
        acct = d["user"]
        pwd = d["pwd"]
        user = session.query(Users).filter_by(acct=acct,pwd=pwd).first()
        if user:
            result = "success"
            msg = "login success"
            resp["token"] = gen_token(user)
    else:
        result = "failure"
        msg = "no account or no passwod information"
    resp["result"] = result
    resp["message"] = msg
    return JsonResponse(resp)



@csrf_exempt
def create_user(request):
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()

    d = json.loads(request.body)
    user_acct = d["user"]
    acct = session.query(Users).filter(Users.acct==user_acct).first()
    result = ""
    msg = ""
    if not acct:
        user_pwd = d["pwd"]
        if "fullname" in d:
            user_fullname = d["fullname"]
        else:
            user_fullname = user_acct

        usr = Users()
        usr.acct = user_acct
        usr.pwd = user_pwd
        usr.fullname = user_fullname
        dt_tz = datetime.datetime.now()
        dt = dt_tz.replace(tzinfo=None)
        usr.created_at = dt
        usr.updated_at = dt
        session.add(usr)
        session.commit()
        result = "success"
        msg = "user created."
    else:
        result = "failure"
        msg = "this account existed."
    resp = {"result": result, "message": msg}
    return JsonResponse(resp)

def list_user(request):
    if not verify_token(request):
        raise exceptions.AuthenticationFailed("token verified failed.")
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()

    users_response = []
    users = session.query(Users).all()
    for usr in users:
        usr = {"account": usr.acct, "fullname": usr.fullname, "created_at": usr.created_at, "updated_at": usr.updated_at}
        users_response.append(usr)
    return JsonResponse({"users": users_response})

@csrf_exempt
def search_user(request):
    if not verify_token(request):
        raise exceptions.AuthenticationFailed("token verified failed.")
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    s = Session()

    result = ''
    msg = ''
    d = json.loads(request.body)
    if "fullname" in d:
        fullname = d["fullname"]
    else:
        result = "failure"
        msg = "fullname is not provided."
    users = []
    user = s.query(Users).filter(Users.fullname==fullname).all()
    if len(user) > 0:
        for usr in user:
            users.append({"account":usr.acct, "fullname":usr.fullname, "created_at":usr.created_at, "updated_at":usr.updated_at})
        result = "ok"
        msg = "{0} user(s) found.".format(len(user))
    else:
        result = "ok"
        msg = "user '{0}' not existed.".format(fullname)

    resp = {"result": result, "message": msg}
    if len(users) > 0:
        resp["users"] = users

    return JsonResponse(resp)
