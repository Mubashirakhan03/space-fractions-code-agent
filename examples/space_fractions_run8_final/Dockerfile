FROM python:3.12-slim
WORKDIR /app
COPY . .
# Tk is needed only for import; tests run headless with xvfb-less skip.
RUN pip install --no-cache-dir pytest
CMD ["python", "-m", "pytest", "-q"]
