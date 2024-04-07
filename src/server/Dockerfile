FROM python:3.11.7

# copy entire project into the working directory

#TODO Optimize this when project layout is no longer a mess
WORKDIR /server
ADD . /server

# install dependencies
RUN pip install poetry
RUN poetry install

# set some default environment variables
ENV PYMONGO_DATABASE_HOST="127.0.0.1"
ENV PYMONGO_DATABASE_PORT=27017

# run the API
CMD ["poetry", "run", "uvicorn","server.main:app","--host","0.0.0.0","--port","2727"]