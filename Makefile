.PHONY: shell

shell:
	docker-compose up -d dev
	docker-compose exec dev bash
