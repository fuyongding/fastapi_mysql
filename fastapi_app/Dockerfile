# venv (clean way)
FROM python:3.10.12

# sets the working directory within the container to /app. All subsequent commands will be executed in this directory.
WORKDIR /app

# set VIRTUAL_ENV variable
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV

# put the bin folder of the virtual environment at the front of the PATH variable in the container
ENV PATH="$VIRTUAL_ENV/bin:$PATH" 

# Copy only the requirements file first
COPY requirements.txt /app/ 

# Install dependencies only if requirements.txt has changed
# requirements.txt changes less frequently so can put this command first
RUN pip install -r requirements.txt 

# Copy the current directory contents into the container at /app
COPY . /app

# Entrypoint script
CMD uvicorn task_manager.main:app --host 0.0.0.0 --port 80

























# Using venv (not that clean, running the binaries)
# FROM python:3.10.12
# WORKDIR /app
# COPY . /app
# RUN python3 -m venv /opt/venv
# RUN . /opt/venv/bin/activate && pip install -r requirements.txt
# CMD . /opt/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 80

# Running without venv
# FROM python:3.10.12
# WORKDIR /app
# COPY . /app
# RUN pip install -r requirements.txt
# ENV MODULE_NAME=main
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]