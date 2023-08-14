#!/bin/bash

# Make sure RabbitMQ is running
sudo systemctl start rabbitmq-server

# Build the docker image
docker build -t python_runner docker/
docker network create --driver=bridge no-internet
docker run -d --name long_running_python_runner --network=no-internet --memory=100m --cpus="0.5" python_runner tail -f /dev/null

# Make sure the redis server is running
redis-server redis-server.conf


#### Services

# Run the code service
nameko run src.services.code_service &

# Run the LLM service
nameko run src.services.llm_service &