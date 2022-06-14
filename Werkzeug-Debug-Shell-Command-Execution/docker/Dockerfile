FROM python:3.6

# install dependency
RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install flask werkzeug

# useradd
RUN useradd robots3

# add chall file to docker
ADD ./prob_src /home/robots3
ADD ./run.sh /home/run.sh
ADD ./flag /flag

# permission setting
RUN chmod 000 /flag
RUN chmod +x /flag

# working
USER robots3
WORKDIR /home/robots3
CMD ["/bin/bash", "/home/run.sh"]