import json
import time
import sqlalchemy, sqlalchemy.orm
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from sqlalchemy import create_engine
from myapp.models import Users, Base
from datetime import datetime

engine = create_engine("postgresql://ui_test:1234@db:5432/ui_test")
Base.metadata.create_all(engine)

def index(request):
    return HttpResponse("Hello, world. You're at the myapp index.\r\n")

def test(request):
    return HttpResponse("test!\r\n")


def get_all_users(session):
    users = session.query(Users).all()
    return users

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
        dt_tz = datetime.now()
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
