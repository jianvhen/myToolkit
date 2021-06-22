#!/bin/env python
# -*- coding:utf-8 -*-

# 从falcon中获取没有指标的机器

import urllib2
import json
import urllib
import json
import requests

url = "http://xxxxx:6031/host/all"

content = urllib2.urlopen(url, timeout=20)
hosts_all = json.loads(content.read())
query_url = "http://xxxxx:9966/graph/history/sum"

def postUrlContent(url, data):
    headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }
    request = requests.post(url, data=json.dumps(data))
    return request.text

ips = []
endpoints = []
ip_endpoint = {}
for item in hosts_all:
    ip = item["ip"]
    endpoint = item["endpoint"]
    ips.append(ip)
    endpoints.append(endpoint)
    ip_endpoint[ip] = endpoint


with open("E:\git\sdp-falcon-plugin\extend_sla\kafka_monitor\hosts.txt") as f:
    for line in f.readlines():
        hangs = line.strip()
        if len(hangs) != 0:
            hang = hangs.split()
            if len(hang) == 1:
                # print(hang[0])
                if hang[0] not in ips:
                    print(hang[0])
                    # continue
                endpoint = ip_endpoint[ip]

                post_data = {
                "start": 1623821465,
                "end": 1623825065,
                "cf": "AVERAGE",
                "endpoint_counters": [{
                    "endpoint": endpoint,
                    "counter": "agent.alive"
                }]
                }
                falcon_result = json.loads(postUrlContent(query_url, post_data))
                result = falcon_result[0]["sum"]
                if result == 0:
                    print(ip,'--',endpoint)
