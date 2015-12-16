SRC_DIR=$(shell readlink -f ../)
PUBLICHTML=$(SRC_DIR)/public_html
CGI=$(SRC_DIR)/cgi-bin
DATA=$(SRC_DIR)/data

pull:
	@docker pull darktal91/tecweb-ubuntu:latest

build:
	@docker build -t tecweb-ubuntu .

stop:
	@docker stop tecweb-server

clean:	stop
	@docker rm tecweb-server

run:
	@docker run -d -p 9999:80 --name=tecweb-server -v $(PUBLICHTML):/var/www/public_html -v $(CGI):/var/www/cgi-bin -v $(DATA):/var/www/data darktal91/tecweb-ubuntu:latest

shell:
	@docker exec -t -i tecweb-server /bin/bash

clean-image:
	@docker rmi darktal91/tecweb-ubuntu:1.0.0

clean-dangling:
	@docker rmi $$(docker images -q --filter="dangling=true")