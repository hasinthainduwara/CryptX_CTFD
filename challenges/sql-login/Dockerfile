FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user
phases
RUN useradd -m ctf
USER ctf

EXPOSE 5000

ENV FLAG="CTF{sql_injection_master_123}"

CMD ["python", "app.py"]
