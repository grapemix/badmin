
sudo -u postgres PGPASSWORD=theory psql -h 127.0.0.1 -U theory -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
