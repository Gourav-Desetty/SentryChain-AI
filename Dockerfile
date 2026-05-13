# select a base image
FROM python:3.12-slim

# set working dir
WORKDIR /app

# Install CPU-only torch FIRST, before everything else
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# copy dependency file
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy apps
COPY . .

# command to run
CMD ["uvicorn", "src.SentryChain.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]