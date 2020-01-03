FROM python:3.7-alpine

# install required libraries
RUN apk update && apk add --no-cache postgresql-dev gcc python3-dev musl-dev curl bash

# expose service port
EXPOSE 8000

# set the working directory
WORKDIR /

# prevent Python from writing out pyc files, disable buffering of stdin/stdout & set python path to /
ENV PYTHONDONTWRITEBYTECODE=1  PYTHONUNBUFFERED=1 PYTHONPATH=/

# copy & install the python requirements
COPY service/requirements/production.txt /requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy the service package
COPY service /service

# create the app user
RUN addgroup -S app && adduser -S app -G app

# chown all the files to the app user
RUN chown -R app:app /service
RUN chmod -R +x /service/entrypoints

# change to the app user
USER app

ENTRYPOINT /service/entrypoints/entrypoint.sh