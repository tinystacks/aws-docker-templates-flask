FROM public.ecr.aws/bitnami/python:3.6
# FROM public.ecr.aws/compose-x/python:3.7

# Create app directory
WORKDIR /

# Bundle app source
COPY . .
RUN rm -rf venv

# Install app dependencies
RUN pip install -r requirements.txt
RUN python3 -m venv venv
# RUN source venv/bin/activate
# RUN flask init-db

# run server
EXPOSE 80
CMD gunicorn --bind 0.0.0.0:80 wsgi:app
