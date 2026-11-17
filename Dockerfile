FROM python:3.12.7-slim
ENV PYTHONUNBUFFERED=1 DATA_DIR=/data
WORKDIR /app
COPY report.py server.py ./
RUN mkdir -p /data
VOLUME ["/data"]
EXPOSE 8080
CMD ["python", "server.py"]
