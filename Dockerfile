# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Set environment variable to run Flask in production mode
ENV FLASK_ENV=production

# Run the Flask app with Gunicorn in production mode
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server:app"]