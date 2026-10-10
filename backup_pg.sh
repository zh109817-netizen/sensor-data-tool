#!/bin/bash
mkdir -p ~/data_tool/pg_backup
docker exec sensor-pg pg_dump -U postgres sensor_db > ~/data_tool/pg_backup/db_$(date +%Y%m%d_%H%M%S).sql
