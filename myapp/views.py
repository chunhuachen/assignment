import json
import time
import jwt
import datetime
import bcrypt
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

        if decode_success:
            if "account" in decoded:
                Session = sqlalchemy.orm.sessionmaker(bind=engine)
                session = Session()

                user = session.query(Users).filter_by(acct=decoded["account"]).first()
                if user:
                    account = decoded["account"]
                    ret = True
                    logger.info("account in token:%r", account)
            else:
                logger.error("User not found")
    return ret, account
    

def user_login(request):
    if not check_request_method(request, 'POST'):
        return JsonResponse({"result": FAILURE, "message": "wrong request method"}, status=405)

    try:
        d = json.loads(request.body)
    except ValueError as e:
        logger.error("body:%r not a json data", request.body)
        return JsonResponse({"result": FAILURE, "message": "wrong request body"}, status=400)

    if "account" in d and "pwd" in d:
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        session = Session()

        acct = d["account"]
        passwd = d["pwd"]
        user = session.query(Users).filter_by(acct=acct).first()
        if user and bcrypt.checkpw(passwd.encode('utf-8'), user.pwd.encode('utf-8')):
            return JsonResponse({"result": SUCCESS, "message": "login success.", "token": gen_token(user)})
        else:
            return JsonResponse({"result": FAILURE, "message": "unauthorized"}, status=401)
    else:
        return JsonResponse({"result": FAILURE, "message": "wrong request body"}, status=400)


def list_user(request):
    if not check_request_method(request, 'GET'):
        return JsonResponse({"result": FAILURE, "message": "wrong request method"}, status=405)

    token_verified, account_in_token = verify_token(request)
    if not token_verified:
        return JsonResponse({"result": FAILURE, "message": "token verification failure"}, status=403)

    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()

    users_response = []
    users = session.query(Users).all()
    for usr in users:
        usr = {"account": usr.acct, "fullname": usr.fullname, "created_at": usr.created_at, "updated_at": usr.updated_at}
        users_response.append(usr)
    return JsonResponse({"result":SUCCESS, "message": SUCCESS, "users": users_response})

def search_user(request):
    if not check_request_method(request, 'POST'):
        return JsonResponse({"result": FAILURE, "message": "wrong request method"}, status=405)

    token_verified, account_in_token = verify_token(request)
    if not token_verified:
        return JsonResponse({"result": FAILURE, "message": "token verification failure"}, status=403)

    try:
        d = json.loads(request.body)
    except ValueError as e:
        logger.error("body:%r not a json data", request.body)
        return JsonResponse({"result": FAILURE, "message": "wrong request body"}, status=400)

    if "fullname" in d:
        fullname = d["fullname"]
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        s = Session()
        users = []
        user = s.query(Users).filter(Users.fullname==fullname).all()
        if len(user) > 0:
            for usr in user:
                users.append({"account":usr.acct, "fullname":usr.fullname, "created_at":usr.created_at, "updated_at":usr.updated_at})
            msg = "{0} user(s) found.".format(len(user))
        else:
            msg = "no user has fullname:'{0}'.".format(fullname)
        resp = {"result": SUCCESS, "message": msg}
        if len(users) > 0:
            resp["users"] = users
        return JsonResponse(resp)
    else:
        return JsonResponse({"result": FAILURE, "message": "fullname not provided."}, status=400)

def user_detail(request, account):
    if not check_request_method(request, 'GET'):
        return JsonResponse({"result": FAILURE, "message": "wrong request method"}, status=405)

    token_verified, account_in_token = verify_token(request)
    if not token_verified:
        return JsonResponse({"result": FAILURE, "message": "token verification failure"}, status=403)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    s = Session()
    user = s.query(Users).filter_by(acct=account).first()
    if user:
        result = SUCCESS
        msg = "query success."
        user_info = {"account": account, "fullname": user.fullname, "created_at": user.created_at, "updated_at": user.updated_at}
        return JsonResponse({"result": result, "message": msg, "user_detail": user_info})
    return JsonResponse({"result": SUCCESS, "message": "no such user."})

def update_user(request):
    if not check_request_method(request, 'PUT'):
        return JsonResponse({"result": FAILURE, "message": "wrong request method"}, status=405)

    try:
        d = json.loads(request.body)
    except ValueError as e:
        logger.error("body:%r not a json data", request.body)
        return JsonResponse({"result": FAILURE, "message": "wrong request body"}, status=400)

    if "account" in d:
        acct = d["account"]
    else:
        return JsonResponse({"result": FAILURE, "message": "no account information."}, status=400)

    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    s = Session()
    user = s.query(Users).filter_by(acct=acct).first()
    if user:
        # the account exist, we should verify its jwt token
        token_verified, account_in_token = verify_token(request)
        if not token_verified:
            return JsonResponse({"result": FAILURE, "message": "token verification failure"}, status=403)
        if acct != account_in_token:
            return JsonResponse({"result": FAILURE, "message": "user mismatch."}, status=400)

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
        return JsonResponse({"result": SUCCESS, "message": "account updated."})

    else:
        # new user
        if "pwd" in d:
            passwd = d["pwd"]
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(passwd.encode('utf-8'), salt)
        else:
            return JsonResponse({"result": FAILURE, "message": "no password information."}, status=400)

        usr = Users()
        usr.acct = acct
        usr.pwd = hashed.decode('utf-8')
        if "fullname" in d:
            user_fullname = d["fullname"]
        else:
            user_fullname = acct
        usr.fullname = user_fullname
        dt_tz = datetime.datetime.now()
        dt = dt_tz.replace(tzinfo=None)
        usr.created_at = dt
        usr.updated_at = dt
        s.add(usr)
        s.commit()
        return JsonResponse({"result": SUCCESS, "message": "account created.", "token": gen_token(usr)}, status=201)

    token_verified, account_in_token = verify_token(request)
    if not token_verified:
        return JsonResponse({"result": FAILURE, "message": "token verification failure"}, status=403)

    # we should check the account from jwt is correct or not
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    s = Session()


    return JsonResponse({"result": SUCCESS, "message": "updated successfully"})

def delete_user(request, account):
    if not check_request_method(request, 'DELETE'):
        return JsonResponse({"result": FAILURE, "message": "wrong request method"}, status=405)

    token_verified, account_in_token = verify_token(request)
    if not token_verified:
        return JsonResponse({"result": FAILURE, "message": "token verification failure"}, status=403)

    logger.info("account:%r", account)

    if account == account_in_token:
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        s = Session()
        user = s.query(Users).filter_by(acct=account).first()
        if user:
            s.delete(user)
            s.commit()
            return JsonResponse({"result": SUCCESS, "message": "deleted successfully"})
        else:
            return JsonResponse({"result": FAILURE, "message": "no such user."}, status=400)
    else:
        #delete your own account only
        return JsonResponse({"result": FAILURE, "message": "user mismatch."}, status=400)
