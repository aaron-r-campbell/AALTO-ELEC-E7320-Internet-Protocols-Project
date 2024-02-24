FROM python:3.11.7

EXPOSE 7777

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# If the code has changed, we only need to rebuild from this step
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7777", "--reload"]