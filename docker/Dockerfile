FROM python:3.12-slim

# Prevents Python from generating .pyc files
# saving space and ensuring the immutability of container.
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures that all output from your Python application 
# is immediately visible in the logs.
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat-openbsd

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

# Run additional commands
RUN chmod +x /app/docker/entrypoint.sh
ENTRYPOINT ["/app/docker/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]