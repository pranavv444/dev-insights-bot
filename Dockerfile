FROM python:3.12.1-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y     gcc     && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Run the bot
CMD ["python", "-m", "src.bot.slack_bot"]
