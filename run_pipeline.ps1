# 1) Start/ensure postgres
docker rm -f retail-postgres | Out-Null
docker run --name retail-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=retail -p 5433:5432 -d postgres:16

Start-Sleep -Seconds 5

# 2) Load raw
$env:PG_HOST="localhost"
$env:PG_PORT="5433"
$env:PG_DB="retail"
$env:PG_USER="postgres"
$env:PG_PASSWORD="postgres"
python .\etl\dataraw_para_SQL.py

# 3) Build layers
Get-Content .\sql\staging.sql | docker exec -i retail-postgres psql -U postgres -d retail
Get-Content .\sql\marts.sql | docker exec -i retail-postgres psql -U postgres -d retail
Get-Content .\sql\quality_checks.sql | docker exec -i retail-postgres psql -U postgres -d retail
