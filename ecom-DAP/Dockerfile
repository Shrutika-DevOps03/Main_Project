FROM python:3.14-slim

WORKDIR /app

COPY api/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ api/

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api.app:app"]
