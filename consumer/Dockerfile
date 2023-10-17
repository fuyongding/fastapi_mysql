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

CMD ["python","-u","consumer.py"]
#CMD python consumer.py