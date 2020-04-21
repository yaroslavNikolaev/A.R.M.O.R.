FROM gcr.io/google-appengine/python
MAINTAINER scy-ther scy-ther@hotmail.com

RUN mkdir armor
COPY ./ /armor

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && apt-get update -y && apt-get install google-cloud-sdk -y

RUN virtualenv -p python3.7 /env
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
RUN pip install -r /armor/requirements.txt

RUN groupadd -g 1010 armor
RUN useradd -g armor -u 8877 armor -m
RUN chown -R armor:armor /armor
RUN chmod -R 740 /armor
USER armor
WORKDIR /armor

ENTRYPOINT ["python" , "./armor.py"]
CMD ["-h"]