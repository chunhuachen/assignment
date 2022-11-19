1. git clone git@github.com:chunhuachen/ui_assignment.git

2. docker compose up

3. Run API:
    Create User:
        curl -d '{"account":<user account>, "pwd":<user passowrd>, "fullname":<full name>}' -H "Content-Type: application/json" -X PUT http://127.0.0.1:8000/myapp/update-user

    Login User:
        curl -d '{"account":<user account>, "pwd":<user passowrd>}' -H "Content-Type: application/json" -X POST http://127.0.0.1:8000/myapp/login-user

    Update User:
        curl -d '{"account":<user account>, "pwd":<the password you want to update>, "fullname":<the full name you want to update>}' -H "Content-Type: application/json" -H "Authorization:Bearer <Token>" -X PUT http://127.0.0.1:8000/myapp/update-user

    Delete User:
        curl -H "Content-Type: application/json" -H "Authorization:Bearer <Token>" -X PUT  http://127.0.0.1:8000/myapp/delete-user/<user account>

    List All Users:
        curl -H "Content-Type: application/json" -H "Authorization:Bearer <Token>" http://127.0.0.1:8000/myapp/list-all-users

    List User Detail:
        curl -H "Content-Type: application/json" -H "Authorization:Bearer <Token>" http://127.0.0.1:8000/myapp/detail/<user account>

    Search User by Full Name:
        curl -d '{"fullname":<full name>" -H "Content-Type: application/json" -H "Authorization:Bearer <Token>" -X POST http://127.0.0.1:8000/myapp/search-user