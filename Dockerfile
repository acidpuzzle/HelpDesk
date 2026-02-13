FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WORKDIR=/helpdesk

VOLUME $WORKDIR

WORKDIR $WORKDIR

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY helpdesk/ .

RUN useradd -U appuser && chown -R appuser:appuser $WORKDIR
USER appuser

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "helpdesk.wsgi:application"]
