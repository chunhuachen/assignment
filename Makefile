crete-table: create-database
	docker exec -it my-postgres psql -U ui_test -c "create table users (acct text primary key, pwd text, fullname text, created_at timestamp, updated_at timestamp);"

create-database: create-postgres
	docker exec -it my-postgres psql -U postgres -c "create role ui_test with login password '1234';"
	docker exec -it my-postgres psql -U postgres -c "create database ui_test owner ui_test;"


create-postgres:
	docker run -d --name my-postgres -p 5432:5432 -e POSTGRES_PASSWORD=admin postgres
	sleep 3

