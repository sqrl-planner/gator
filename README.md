# gator
Central dataset aggregator and content manager for sqrl planner

 ## Running the server
 You'll need to have [Docker installed](https://docs.docker.com/get-docker/).

 #### Clone this repo and move into the directory
 ```shell
 git clone https://github.com/sqrl-planner/gator.git
 cd gator
 ```

 #### Copy starter files
 ```shell
 cp .env.example .env
 ```
 The defaults are for running in *development* mode. Go through each variable in the file and make sure it is properly set. You will likely need to update the credentials.

 #### Build the Docker image and start the Docker container

You start the Docker container by running

 *The first time you run this, it's going to take 5-10 minutes depending on your internet connection and hardware.*
 ```shell
 docker-compose up
 ```
 This will build the image, if needed, and once built, automatically spin up a container with the image. If you'd like to force a rebuild of the image, you may additionally pass an optional ``--build`` flag to the above command.

 #### Stopping the Docker container

 You can stop running the container by running ``docker-compose down``.

#### Setting up the database

gator uses MongoDB, a NoSQL database program. An instance of MongoDB is already setup for you (with a ``gator`` database) by the Docker container. 

Alterntively, you can run an instance locally or use a number of database providers. If you do so, create an empty database on your MongoDB instance and update the ``.env`` file with your instance information (host, credentials, and db name).

#### Pulling and syncing data

If your database is empty, you'll need timetable information to use gator. To pull the latest data from all dataset sources, in the Docker container run
```shell
flask sync
```

The Docker container will automaticlly sync the data on the first-run. You might find it useful to setup a cron job to periodically run this job in production.

Currently, the dataset sources are hardcoded parameters in the [``config/settings.py``](https://github.com/sqrl-planner/sqrl-server/blob/main/config/settings.py) file. You must modify this file directly to customize the data sources.

## Native Development Environment
If you prefer to work natively, rather than bootstraping the application in a Docker container, see the [native development workflow](docs/develop-native.md) docs for setup instructions.

## Tools

#### Linting the codebase
```
flake8
```

#### Formatting the codebase
```
autopep8 --in-place --recursive .
```

#### Running tests
````
pytest tests/
````
