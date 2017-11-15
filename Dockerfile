FROM python:3.6
MAINTAINER lulu@guo
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "test.py"]