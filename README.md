1. git clone git@github.com:chunhuachen/ui_assignment.git

2. docker compose up

3. Run API:
    Create User:
        PUT /myapp/create-user

        curl -d '{"account":<user account>, "pwd":<user passowrd>, "fullname":<full name>}' -H "Content-Type: application/json" -X PUT http://127.0.0.1:8000/myapp/create-user


    Login User:
        POST /myapp/login-user

        curl -d '{"account":<user account>, "pwd":<user passowrd>}' -H "Content-Type: application/json" -X POST http://127.0.0.1:8000/myapp/login-user


    Update User:
        PUT /myapp/update-user

        curl -d '{"account":<user account>, "pwd":<the password you want to update>, "fullname":<the full name you want to update>}' -H "Content-Type: application/json" -H "Authorization:Bearer <Token>" -X PUT http://127.0.0.1:8000/myapp/update-user


    Delete User:
        DELETE /myapp/delete-user/<user account>

        curl -H "Content-Type: application/json" -H "Authorization:Bearer <Token>" -X DELETE  http://127.0.0.1:8000/myapp/delete-user/<user account>


    List All Users:
        GET /myapp/list-all-users?order_by=<'account' or 'fullname'>&records_per_page=<records per page>&page_id=<page id>

        curl -H "Content-Type: application/json" -H "Authorization:Bearer <Token>" http://127.0.0.1:8000/myapp/list-all-users


    List User Detail:
        GET /myapp/detail/<user account>

        curl -H "Content-Type: application/json" -H "Authorization:Bearer <Token>" http://127.0.0.1:8000/myapp/detail/<user account>


    Search User by Full Name:
        POST /myapp/search-user

        curl -d '{"fullname":<full name>" -H "Content-Type: application/json" -H "Authorization:Bearer <Token>" -X POST http://127.0.0.1:8000/myapp/search-user


# To run unit test
    docker exec -it <container name> python manage.py test

 example:
    docker exec -it ui_assignment-web-1 python manage.py test
