FROM python:3.6
COPY . /app
WORKDIR /app
RUN pip install "pip >=18.0,<19.0"
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "bin/upload.py"]
CMD ["dummy.txt"]
