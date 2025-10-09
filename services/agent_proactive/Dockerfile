FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the shared library
COPY shared/ /app/shared/

# Copy the agent-specific files
COPY services/agent_proactive/main.py /app/
COPY services/agent_proactive/requirements.txt /app/

# Install dependencies
RUN pip install -r requirements.txt

# Command to run the application
CMD ["python", "main.py"]