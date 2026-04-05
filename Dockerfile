# select a base image
FROM python:3.12-slim

# set working dir
WORKDIR /app

# copy dependency file
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy apps
COPY . .

# command to run
CMD ["uvicorn", "src.SentryChain.api.app:app", "--host", "0.0.0.0", "--port", "8000"]