FROM python:3.11

# -------------------------------
# IF one decides to use python:3.11-slim we need the lines below. This is required for the RDkit
# I sswithed to the non-slim python package and that resolved the lib issue but will keep these commets for reference.
# RDKit is a C++ library with Python bindings — and its Python wheels often link against native system libraries.
# RDKit drawing module (rdMolDraw2D) relies on X11 libraries for rendering. They are essential for Linux deployments.
# ------------------------------
 # -y assumes yes to all prompts
#RUN apt-get update && apt-get install -y \
#    libxrender1 \
#    libxext6 \
#    libexpat1 \
#    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/prd.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["gunicorn", "--workers=3", "--threads=1", "-b", "0.0.0.0:8050", "levseq_dash.app.main_app:server"]
# example to pverride the CMD on the commad line after the image has been created
# in this example I changed the number of workers for gunicorn
# docker run -p 8050:8050 <image-name>> gunicorn --workers 1 --bind 0.0.0.0:8050 levseq_dash.app.main_app_test:server

# remmeber to docker build --platform=linux/arm64   for arm64