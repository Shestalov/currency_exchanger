FROM python:3.9.12

COPY ./requirements.txt /flask_exchanger/requirements.txt
WORKDIR /flask_exchanger
RUN pip install -r requirements.txt

COPY . /flask_exchanger
EXPOSE 5000
CMD ["python", "./main.py"]