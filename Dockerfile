FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libgeos-dev libproj-dev gdal-bin && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "src/build_dataset_and_analysis.py"]
