FROM python:3.6.4-alpine

# Update
RUN apk add --update python py-pip

# Bundle app source
COPY * /

# Install app dependencies
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "/main.py"]
