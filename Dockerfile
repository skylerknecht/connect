#
FROM python:bullseye

#
RUN mkdir /connect
ADD connect /connect/connect
ADD requirements.txt /connect/
ADD resources /connect/resources

# install packages
RUN pip install -r /connect/requirements.txt

# 
ADD dockerBin/start.sh /connect/
ADD dockerBin/server.sh /connect/
RUN chmod +x /connect/start.sh
RUN chmod +x /connect/server.sh

# Shared folder between host
RUN mkdir /data

#
ENTRYPOINT /connect/start.sh
