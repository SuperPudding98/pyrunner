FROM python:3.8

# for convinience only, not needed for pyrunner
RUN pip install ipython

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY pyrunner ./pyrunner

CMD ["bash"]
