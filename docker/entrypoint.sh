#!/bin/sh

# Wait fo the database to be ready
while ! nc -z db 5432; do
  sleep 1
done

# Run management commands
python manage.py createexchangerecords
python manage.py createstockassets
python manage.py createcryptoassets 20
python manage.py importcryptoprices
python manage.py importstockprices

# Start the server
exec "$@"