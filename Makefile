.PHONY: setup install migrate seed check schema test verify run clean

setup:
	./setup.sh

install:
	python -m pip install -r requirements.txt

migrate:
	python manage.py migrate

seed:
	python manage.py seed_demo

check:
	python manage.py check
	python manage.py makemigrations --check --dry-run

schema:
	python manage.py spectacular --file schema.yml --validate

test:
	python manage.py test

verify:
	./verify.sh

run:
	./run.sh

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	rm -f schema.yml
