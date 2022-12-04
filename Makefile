build:
	docker build  . --rm -t app
start:
	docker run --rm -it -e PORT_APP=3000 \
	-e USER_SERVICE_URL=<database_password> \
	--name app -p 3000:3000 app
test:
	docker build  -f Dockerfile.test . --rm  -t app-test
	docker run --rm -it app-test
