FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY discord_bot/ discord_bot/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "-m", "discord_bot.bot"]
