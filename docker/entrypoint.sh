#!/bin/sh
set -e

echo "Waiting for database at $DB_HOST:$DB_PORT ..."
until python -c "import os, psycopg; psycopg.connect(host=os.environ['DB_HOST'], port=os.environ['DB_PORT'], dbname=os.environ['DB_NAME'], user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD']).close()" 2>/dev/null; do
    echo "  database unavailable, retrying in 1s ..."
    sleep 1
done
echo "Database is up."

echo "Applying migrations ..."
python manage.py migrate --noinput

# Seed property data only once: import when the table is empty so that
# container restarts/redeploys do not create duplicate properties.
ALREADY_SEEDED=$(python manage.py shell -c "from property_app.models import Property; print(Property.objects.exists())" | tail -n 1)

if [ "$ALREADY_SEEDED" = "False" ]; then
    echo "No properties found - importing from data/vacation_rentals.csv ..."
    python manage.py import_properties data/vacation_rentals.csv
else
    echo "Properties already exist - skipping import."
fi

exec "$@"
