#!/bin/bash

for i in `seq 1 100`
do

echo "start:", $i

cd /data/docker_config/node0-cl-dev-mqcluster-sdp-rabbitmq-api-sraohm && docker_control run -c docker.conf
sleep 15

/usr/bin/python2.7 /root/rabbitmq.py

done