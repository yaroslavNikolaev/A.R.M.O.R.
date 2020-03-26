FROM python:3.7.7-slim-buster
RUN mkdir armor
COPY ./ /armor
EXPOSE $PORT
RUN pip install -r /armor/requirements.txt
CMD python /armor/armor.py -p $PORT