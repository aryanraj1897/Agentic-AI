FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /sandbox

# Install required data science packages
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scipy \
    scikit-learn

COPY runner.py /sandbox/runner.py

RUN useradd -m sandboxuser
USER sandboxuser

ENTRYPOINT ["python", "/sandbox/runner.py"]
