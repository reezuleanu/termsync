FROM python:3.11.7


WORKDIR /server
ADD ./src/server /server/src/server/
ADD requirements.txt /server

# install dependencies
RUN pip install -r requirements.txt

# set some default environment variables
ENV PYMONGO_DATABASE_HOST="127.0.0.1"
ENV PYMONGO_DATABASE_PORT=27017

# run the API
CMD ["uvicorn","src.server.main:app","--host","0.0.0.0","--port","2727"]