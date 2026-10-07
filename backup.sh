#!/bin/bash
mkdir -p ~/data_tool/backup
cp ~/data_tool/daily_report.csv ~/data_tool/backup/daily_report_$(date +%Y%m%d_%H%M%S).csv
