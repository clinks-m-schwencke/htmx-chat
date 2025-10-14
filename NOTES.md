# NOTES

## Setting up a dev environment

First, you need to create a virtual environment for development.

>:::
We will be using docker to launch the server, but also having a virtual environment can be
convenient for development (LSPs in editor, etc.)
:::

Create a virtual environment in a fixed place, NOT within the project folder.
If the project files are moved, the virtual environment will stop working, so a fixed place for virtual 
environment is highly recommended. 

If you haven't already, create a directory for virtual environments in your home folder like so.
```sh
mkdir ~/.virtualenvs
```

Then, with a modern python version (>=3.4) you can use the builtin `venv` module to create a 
virtual environment. You should name the environment after the project it is for.

```sh
python3 -m venv ~/.virtualenvs/{env_name}
```

Then, to activate the environment, you need to source it.

```sh
source ~/.virtualenvs/{env_name}/bin/activate
```

It can be convenient to wrap the above command in a script and place it in your project folder.
If all developers place their environment in the same directory, eveyone can use it!

```sh
source venv.sh
```


## Creating a django project
Before we start setting up docker, we need to create the project for docker to launch.
First we will install django into our virtual environment.

> Make sure that you have activated your virtual environment. 
If your terminal begins with `({env_name})` then it is active. If not, activated it with the above
commands.

```sh
# Install latest version of django
pip install django
# If you want to install a specific version
pip install django==5.2.7
```

We'll also install the database driver for PostgreSQL.

```sh
pip install "psycopg[binary]"
```

Next, we will use django to create the project scaffolding. The following command will create a project
in the folder `django_project`. 

```sh
django-admin startproject django_project .
```

Now that the project has been created, we can edit django's settings to use PostgreSQL as our database.
Change the `DATABASES` variable from its default to the following.
```py
# django_project/settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "db",  # set in docker-compose.yml
        "PORT": 5432,  # default postgres port
    }
}
```

The last thing to do before switching over to docker, is to save the dependecies in a lockfile. 
This command will put all of the dependencies into a `requirements.txt` file, which docker will use to 
install the correct packages.

```sh
pip freeze > requirements.txt
```

We are finished with the virtual environment for now, so you can deactivate it with the following command.
```sh
deactivate
```

To make sure that the environment is not longer active, check that there are no brackets in the terminal, 
and try to run a django command.
```sh
$python manage.py runserver
File "/Users/wsv/Desktop/django-docker/manage.py", line 11, in main
  from django.core.management import execute_from_command_line
ModuleNotFoundError: No module named 'django'
```

This error message means that the environment is deactivated, and we're ready to start configuring docker.


## Setting up Docker

### DockerFile

First, we need to set up our Dockerfile

```dockerfile
# Get latest python slim image
FROM python:3.13.3-slim-bullseye

# Set environmet variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .
```

We get the lastest python 'slim' image, to keep size low.

Then, we use the `ENV` command to set three environment variables:

`PIP_DISABLE_PIP_VERSION_CHECK` turns off an automatic check for pip updates each time
`PYTHONDONTWRITEBYTECODE` means Python will not try to write .pyc files
`PYTHONUNBUFFERED` ensures Docker does not buffer our console output

The command `WORKDIR` sets the default working directory for the rest of the commands.

Next, we install the dependencies with `pip`, based on our `requirements.txt`
We copy the requirements file to the docker container, then run pip install.

Finally, we copy all of the code files into the container.

### .dockerignore
```gitignore
# .dockerignore
.venv
.git
.gitignore
```

### docker-compose
```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code 
  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - "POSTGRES_HOST_AUTH_METHOD=trust"

volumes:
  postgres_data:
```

### Starting docker

Now we are ready to run the docker container!
First we build the container with this command.
```sh
docker build .
```

Then we launch the container with docker compose.
```sh
docker compose up
```

Now that the container is running, we need to run a database migration.
It's recommended to migrate after the model is written, but we will do it now.
```sh
docker exec -it {CONTAINER}-web-1 python manage.py migrate
```

And here is how to create an admin user.
```sh
docker exec -it {CONTAINER}-web-1 python manage.py createsuperuser
```

## Creating a new Django App
To create a new app, run the following command in docker

```sh
docker exec -it {CONTAINER} python manage.py startapp {PROJECT_NAME}
```

For example:
```sh
docker exec -it htmx-chat-web-1 python manage.py startapp chat
```

>:::
Docker exec flags
i = "Interactive", keeps the STDIN open
t = Allocates a pseudo TTY
:::


