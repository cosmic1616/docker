# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME TelegramBot

# Run bot.py when the container launches
CMD ["python", "bot.py"]
