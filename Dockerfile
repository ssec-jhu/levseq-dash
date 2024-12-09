FROM python:3.11-slim

WORKDIR /app

COPY requirements/prd.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["gunicorn", "--workers=1", "--threads=1", "-b", "0.0.0.0:8050", "levseq_dash.app.main_app_test:server"]
