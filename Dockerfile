FROM python:3.12.7-slim
ENV PYTHONUNBUFFERED=1 DATA_DIR=/data PORT=8080
WORKDIR /app
COPY report.py server.py healthcheck.py ./
RUN mkdir -p /data
VOLUME ["/data"]
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 CMD ["python", "healthcheck.py"]
CMD ["python", "server.py"]
