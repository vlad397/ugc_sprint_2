SHELL = /bin/sh
CURRENT_UID := $(shell id -u)

shell:
	docker-compose exec ugc_api bash

format:
	docker run --rm -v $(CURDIR):/data cytopia/black . -l 120 -t py38
	docker run --rm -v $(CURDIR):/data chelovek/cisort --profile black --line-length 120 .

mongo_setup_cluster:
	docker exec -it mongocfg1 bash -c "cat /scripts/init_mongocfg1.js | mongosh"
	docker exec -it mongors1n1 bash -c "cat /scripts/init_mongors1n1.js | mongosh"
	docker exec -it mongors2n1 bash -c "cat /scripts/init_mongors2n1.js | mongosh"
	sleep 20
	docker exec -it mongos1 bash -c "cat /scripts/init_mongos1.js | mongosh"
