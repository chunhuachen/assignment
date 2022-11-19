import json
import time
import jwt
import datetime
import sqlalchemy, sqlalchemy.orm
import logging
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from sqlalchemy import create_engine
from myapp.models import Users, Base
from rest_framework import exceptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUCCESS = "success"
FAILURE = "failure"

engine = create_engine(settings.DATABASE_ENGINE)
Base.metadata.create_all(engine)

def check_request_method(request, method):
    if request.method != method:
        return False
    return True

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
    logger.info('encoded_jwt:%r', encoded_jwt)
    return encoded_jwt

def verify_token(request):
    return True, ''
    account = None
    ret = False
    decode_success = False
    authorization_header = request.headers.get("Authorization")
    if authorization_header:
        try:
            access_token = authorization_header.split(" ")[1]
            decoded = jwt.decode(access_token.encode("utf-8"), settings.SECRET_KEY, algorithms=["HS256"])
            decode_success = True
        except jwt.ExpiredSignatureError:
            logger.error("access_token expired")
        except IndexError:
            logger.error("Token prefix missing")

        if decode_success and "account" in decoded:
            Session = sqlalchemy.orm.sessionmaker(bind=engine)
            session = Session()

            user = session.query(Users).filter_by(acct=decoded["account"]).first()
            if user:
                account = decoded["account"]
                ret = True
                logger.info("account in token:%r", account)
        else:
            log.error("User not found")
    return ret, account
    

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
    token_verified, account_in_token = verify_token(request)
    if not token_verified:
        raise exceptions.AuthenticationFailed("token verified failed.")
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()

    users_response = []
    users = session.query(Users).all()
    for usr in users:
        usr = {"account": usr.acct, "fullname": usr.fullname, "created_at": usr.created_at, "updated_at": usr.updated_at}
        users_response.append(usr)
    return JsonResponse({"users": users_response})

def search_user(request):
    token_verified, account_in_token = verify_token(request)
    if not token_verified:
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

def user_detail(request, account):
    if not check_request_method(request, 'GET'):
        return JsonResponse({"result": FAILURE, "msg": "wrong request method"}, status=405)

    token_verified, account_in_token = verify_token(request)
    if not token_verified:
        return JsonResponse({"result": FAILURE, "msg": "token verification failure"}, status=403)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    s = Session()
    user = s.query(Users).filter_by(acct=account).first()
    if user:
        result = SUCCESS
        msg = "query success."
        user_info = {"account": account, "fullname": user.fullname, "created_at": user.created_at, "updated_at": user.updated_at}
        return JsonResponse({"result": result, "msg": msg, "user_detail": user_info})
    return JsonResponse({"result": SUCCESS, "msg": "no such user."})

def update_user(request):
    if not check_request_method(request, 'PUT'):
        return JsonResponse({"result": FAILURE, "msg": "wrong request method"}, status=405)

    token_verified, account_in_token = verify_token(request)
    if not token_verified:
        return JsonResponse({"result": FAILURE, "msg": "token verification failure"}, status=403)

    d = json.loads(request.body)
    # we should check the account from jwt is correct or not
    acct = d["account"]
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    s = Session()

    user = s.query(Users).filter_by(acct=acct).first()
    if user:
        updated = False
        if "pwd" in d:
            user.pwd = d["pwd"]
            updated = True
        if "fullname" in d:
            user.fullname = d["fullname"]
            updated = True
        if updated:
            dt_tz = datetime.datetime.now()
            dt = dt_tz.replace(tzinfo=None)
            user.updated_at = dt
        s.commit()

    return JsonResponse({"result": SUCCESS, "msg": "updated successfully"})

def delete_user(request, account):
    if not check_request_method(request, 'DELETE'):
        return JsonResponse({"result": FAILURE, "msg": "wrong request method"}, status=405)

    token_verified, account_in_token = verify_token(request)
    if not token_verified:
        return JsonResponse({"result": FAILURE, "msg": "token verification failure"}, status=403)

    logger.info("account:%r", account)

    if account == account_in_token:
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        s = Session()
        user = s.query(Users).filter_by(acct=account).first()
        if user:
            s.delete(user)
            s.commit()
            return JsonResponse({"result": SUCCESS, "msg": "deleted successfully"})
        else:
            return JsonResponse({"result": FAILURE, "msg": "no such user."}, status=400)
    else:
        #delete your own account only
        return JsonResponse({"result": FAILURE, "msg": "user mismatch."}, status=400)
