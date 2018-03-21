FROM python:3.6.4-alpine

# Update
RUN apk add --update python py-pip

# Bundle app source
RUN mkdir /app
WORKDIR /app
ADD . /app

# Install app dependencies
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "/src/main.py"]
