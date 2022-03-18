test-env-setup:

	docker run -d \
	-p 5432:5432 \
	-e POSTGRES_PASSWORD=pass \
	-e POSTGRES_USER=user \
	-e POSTGRES_DB=db \
	postgres:14 

test-run:

	DATABASE_URL=postgres://user:pass@localhost:5432/db