FROM python:3.10

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /project
WORKDIR /project



ENTRYPOINT ["python"]
CMD ["main.py"]

