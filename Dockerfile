FROM python:3.6

# Create app directory
WORKDIR /

# Bundle app source
COPY . .

# Install app dependencies
RUN pip install -r requirements.txt

EXPOSE 8000
CMD flask run -p 8000 --host 0.0.0.0