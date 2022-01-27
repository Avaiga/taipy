# Deploy a Dockerize Taipy application with Heroku

## Prerequisites

- Minimal knowledge in Docker.
- Docker should be installed. Check [the official documentation](https://docs.docker.com/engine/install/) for docker installation.
- [:material-arrow-right: Prepare your Taipy application](../prepare-taipy-for-deployment.md)
- [:material-arrow-right: Set up your Heroku environment](setup.md)


## 1. Create your Dockerfile

Besides your application, you should create a `Dockerfile` that will allow Docker to build your container.

Here is an example with `main.py` as the entry point of your application and `requirements.txt` file with all your dependencies (Taipy included):

```
# Your Python version
FROM python:3.9

# Install your application
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

# Start up command
CMD python demo8.py
```

### Note

This Dockerfile is provided as an example and tested without security consideration, do not use it for a production environment.


## 2. Build and test your Docker

At the same place of your Dockerfile, run the following command to create a Docker image named **<my-taipy-app>**: `docker build . -t <my-taipy-app>`

You can now run it with the command line: `docker run -p 5000:5000 -d --name <my-taipy-app> <my-taipy-app>`

Open your browser and go on [http://localhost:5000](http://localhost:5000) -- a start up time can be present --.

## 3. Deployment

In our example, we use the name `<my-taipy-app>` for our application. On Heroku, this name should be unique. So you should replace it everywhere by a custom value.

```
heroku login
heroku create <my-taipy-app>
heroku container:login
heroku container:push web -a <my-taipy-app>
heroku config:set CLIENT_URL="https://<my-taipy-app>.herokuapp.com" -a <my-taipy-app>
heroku container:release web -a <my-taipy-app>
```

## 4. Check your deployment

You can go on the url `https://<my-taipy-app>.herokuapp.com` with your browser or run `heroku open -a <my-taipy-app>`. Your application should be deployed correctly.


## 5. Clean your resources

Stop the local docker container: `docker stop <my-taipy-app>`

Remove the local docker container: `docker rm <my-taipy-app>`

Remove the local docker image: `docker rmi <my-taipy-app>`

Remove the Heroku application: `heroku apps:destroy <my-taipy-app> --confirm <my-taipy-app>`
