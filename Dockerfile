FROM python:3.12-slim
WORKDIR /app
COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt
COPY fast_avg.py app.py sensor_data.csv ./
EXPOSE 8000
CMD ["python", "app.py"]
