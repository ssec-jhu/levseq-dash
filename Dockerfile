FROM python:3.11-slim

WORKDIR /app

COPY requirements/prd.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["gunicorn", "--workers=3", "--threads=1", "-b", "0.0.0.0:8050", "levseq_dash.app.main_app:server"]
# example to pverride the CMD on the commad line after the image has been created
# in this example I changed the number of workers for gunicorn
# docker run -p 8050:8050 <image-name>> gunicorn --workers 1 --bind 0.0.0.0:8050 levseq_dash.app.main_app_test:server