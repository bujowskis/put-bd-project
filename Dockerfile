FROM python:3.9-slim

WORKDIR /app

# prepare python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# prepare resources
## data and server
COPY init_db.py .
COPY data/dataset.csv dataset.csv
COPY bookkeeper_functions.py .
COPY flask_server.py .
## html template
COPY bookkeeper.html templates/
## static files for the html
COPY action_scripts.js static/
COPY bookkeeper.css static/
## run script
COPY run.sh .

# setup app
RUN chmod +x init_db.py
RUN chmod +x flask_server.py
RUN chmod +x run.sh

EXPOSE 8089
CMD ["./run.sh"]
