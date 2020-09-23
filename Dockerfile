FROM python:3.8

# for convinience only, not needed for pyrunner
RUN pip install ipython
RUN apt-get update; apt-get install -y vim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY pyrunner ./pyrunner
COPY pyrunnerd ./

CMD ["bash"]
