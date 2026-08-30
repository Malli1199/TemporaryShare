From python:3.19-slim

Workdir /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY index.html .

Expose 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]