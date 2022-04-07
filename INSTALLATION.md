# Installation, Configuration and Run

## Installation
1. Clone the taipy rest repository
```
$ git clone https://github.com/Avaiga/taipy-rest
```
2. Enter taipy rest directory

```
$ cd taipy-rest
```

3. Install dependencies
```
$ pip install pipenv && pipenv install
```

## Configuration
Before running, we need to define some variables. Taipy rest APIs depend on pre-configuration of taipy config objects, 
i.e, is mandatory to define all configuration of DataNodes, Tasks, Pipelines, etc. The file containing this 
configuration needs to be passed to the application at runtime. The following variable needs to be defined:
 - TAIPY_SETUP_FILE: the path to the file containing all of taipy object configuration

If using Docker, the folder containing the file needs to be mapped as a volume for it to be accessible to the 
application.

## Running
To run the application you can either run locally with:
```
$ flask run
```

or it can be run inside Docker with:
```
$ docker-compose up
```

You can also run with a Gunicorn or wsgi server.

### Running with Gunicorn
This project provide a simple wsgi entry point to run gunicorn or uwsgi for example.

For gunicorn you only need to run the following commands

```
$ pip install gunicorn

$ gunicorn myapi.wsgi:app
```
And that's it ! Gunicorn is running on port 8000

If you chose gunicorn as your wsgi server, the proper commands should be in your docker-compose file.

### Running with uwsgi
Pretty much the same as gunicorn here

```
$ pip install uwsgi
$ uwsgi --http 127.0.0.1:5000 --module myapi.wsgi:app
```

And that's it ! Uwsgi is running on port 5000

If you chose uwsgi as your wsgi server, the proper commands should be in your docker-compose file.

### Deploying on Heroku
Make sure you have a working Docker installation (e.g. docker ps) and that you’re logged in to Heroku (heroku login).

Log in to Container Registry:

```
$ heroku container:login
```

Create a heroku app
```
$ heroku create
```

Build the image and push to Container Registry:
```
$ heroku container:push web
```

Then release the image:
```
$ heroku container:release web
```

You can now access **taipy rest** on the URL that was returned on the `heroku create` command.

## Documentation

All the API Documentation can be found, after running the application in the following URL:
 - ```/redoc-ui``` ReDoc UI configured to hit OpenAPI yaml file
 - ```/openapi.yml``` return OpenAPI specification file in yaml format