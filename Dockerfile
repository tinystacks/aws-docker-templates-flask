# FROM python:3.6
FROM public.ecr.aws/bitnami/python:3.6
COPY --from=public.ecr.aws/tinystacks/secret-env-vars-wrapper:latest-x86 /opt /opt
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.3.2-x86_64 /lambda-adapter /opt/extensions/lambda-adapter

# Create app directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install app dependencies
RUN apt-get update
RUN echo Y | apt-get install libpq-dev python-dev
RUN pip install -r requirements.txt

# start the virtual environment
RUN python3 -m venv venv

# Copy the whole folder inside the Image filesystem
COPY . .

EXPOSE 8000

CMD /opt/tinystacks-secret-env-vars-wrapper gunicorn --bind 0.0.0.0:8000 wsgi:app
