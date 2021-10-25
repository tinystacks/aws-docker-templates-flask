# FROM python:3.6
FROM public.ecr.aws/bitnami/python:3.6

# Create app directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install app dependencies
RUN pip install -r requirements.txt

# start the virtual environment
RUN python3 -m venv venv

# Copy the whole folder inside the Image filesystem
COPY . .

EXPOSE 80

CMD gunicorn --bind 0.0.0.0:80 wsgi:app
