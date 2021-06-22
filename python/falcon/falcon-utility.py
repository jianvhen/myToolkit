#!/bin/env python
# -*- coding:utf-8 -*-

# 从falcon中获取低负载的机器信息, 并写到excel中

# 判断低负载机器条件, 时间范围定在早8点到晚8点
# 2021-06-7:08:00:00  1623024000
# 2021-06-7:20:00:00  1623067200
# 1.服务器平均CPU使用率<=10%（一天）  cpu.busy < 10
# 2.服务器平均内存使用率<=30%（一天）  mem.memused.percent < 30
# 3.服务器数据磁盘使用率低于30%       df.bytes.used.percent/fstype=xfs,mount=/data  <= 30

import urllib2
import urllib
import json
import requests
import xlwt
import time


start_time = 1623974400
end_time_1d = 1624017600
start_time_1w = 1623945600
end_time_1w = 1624118400
one_day_count = 1440
cpu_percentage = 10
mem_percentage = 30
data_percentage = 30
host_url = "http://xxxxx/host/all"
query_url = "http://xxxxx/graph/history/sum"



# excel 相关
def createExcelAll(workbook):
    # workbook = xlwt.Workbook()
    sheet1 = workbook.add_sheet('all_info',cell_overwrite_ok=True)
    sheet1.write(0,0,'ip')
    sheet1.write(0,1,'enpoint')
    sheet1.write(0,2,'cpu_used_percent_1d_average')
    sheet1.write(0,3,'mem_used_percent_1d_average')
    sheet1.write(0,4,'data_used_percent_1d_average')
    sheet1.write(0,5,'cpu_used_percent_1w_average')
    sheet1.write(0,6,'mem_used_percent_1w_average')
    sheet1.write(0,7,'data_used_percent_1w_average')
    return sheet1

def createExcelLow(workbook):
    # workbook = xlwt.Workbook()
    sheet2 = workbook.add_sheet('low_info',cell_overwrite_ok=True)
    sheet2.write(0,0,'ip')
    sheet2.write(0,1,'enpoint')
    sheet2.write(0,2,'cpu_used_percent_1d_average')
    sheet2.write(0,3,'mem_used_percent_1d_average')
    sheet2.write(0,4,'data_used_percent_1d_average')
    sheet2.write(0,5,'cpu_used_percent_1w_average')
    sheet2.write(0,6,'mem_used_percent_1w_average')
    sheet2.write(0,7,'data_used_percent_1w_average')
    return sheet2

def saveExcel(workbook):
    workbook.save('./falcon_load.xls')

all_line = 1
low_line = 1
def writeDataExcel(sheet, sheet_type, ip, endpoint, cpu_used_1d, mem_used_1d, df_used_1d, cpu_used_1w, mem_used_1w, df_used_1w):
    if sheet_type == "all":
        global all_line
        sheet.write(all_line,0,ip)
        sheet.write(all_line,1,endpoint)
        sheet.write(all_line,2,cpu_used_1d)
        sheet.write(all_line,3,mem_used_1d)
        sheet.write(all_line,4,df_used_1d)
        sheet.write(all_line,5,cpu_used_1w)
        sheet.write(all_line,6,mem_used_1w)
        sheet.write(all_line,7,df_used_1w)
        all_line += 1
    if sheet_type == "low":
        global low_line
        sheet.write(low_line,0,ip)
        sheet.write(low_line,1,endpoint)
        sheet.write(low_line,2,cpu_used_1d)
        sheet.write(low_line,3,mem_used_1d)
        sheet.write(low_line,4,df_used_1d)
        sheet.write(low_line,5,cpu_used_1w)
        sheet.write(low_line,6,mem_used_1w)
        sheet.write(low_line,7,df_used_1w)
        low_line += 1




# FALCON 相关
# content = urllib2.urlopen(host_url, timeout=20)
# hosts_all = json.loads(content.read())

def getUrlContent(url):
    content = urllib2.urlopen(host_url, timeout=20)
    return json.loads(content.read())


def postUrlContent(url, data):
    headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }
    request = requests.post(url, data=json.dumps(data))
    return request.text

def main(sheet_all, sheet_low):
    for item in getUrlContent(host_url):
        ip = item["ip"]
        if "172.24" in ip:
            continue
        if "192.168" in ip:
            continue

        # if ip != "10.33.9.180":
        #     continue

        endpoint = item["endpoint"]
        print("ip:%s,endpoint:%s" % (ip, endpoint))
        cpu_busy_1d = 0
        mem_used_1d = 0 
        data_xfs_used_1d = 0 
        data_ext4_used_1d = 0 
        cpu_busy_1w = 0 
        mem_used_1w = 0 
        data_xfs_used_1w = 0
        data_ext4_used_1w = 0
        df_used_1d = 0
        df_used_1w = 0
        
        post_data_1d = {
            "start": start_time,
            "end": end_time_1d,
            "cf": "AVERAGE",
            "endpoint_counters": [{
                "endpoint": endpoint,
                "counter": "cpu.idle"
            },{
                "endpoint": endpoint,
                "counter": "mem.memused.percent"
            },{
                "endpoint": endpoint,
                "counter": "df.bytes.used.percent/fstype=xfs,mount=/data"
            },{
                "endpoint": endpoint,
                "counter": "df.bytes.used.percent/fstype=ext4,mount=/data"
            }]
        }
        falcon_result = json.loads(postUrlContent(query_url, post_data_1d))
        # print("falcon reslut: %s" % falcon_result)
        cpu_flag = False
        mem_flag = False
        data_flag = False
        for i in range(3):
            try:
                # print(falcon_result[i])
                step = falcon_result[i]["step"]
                if step == 30:
                    point = 2
                else:
                    point = 1
                if falcon_result[i]["counter"] == "cpu.idle":
                    cpu_busy_1d = 100 - (falcon_result[i]["sum"]/ (720 * point))
                    if cpu_busy_1d < cpu_percentage:
                        cpu_flag = True
                    # print("cpu_busy: ", falcon_result[i]["sum"]/1440)
                if falcon_result[i]["counter"] == "mem.memused.percent":
                    # print("mem.memused.percent: ", falcon_result[i]["sum"]/1440)
                    mem_used_1d = falcon_result[i]["sum"]/ (720 * point)
                    if mem_used_1d < mem_percentage:
                        mem_flag = True
                if falcon_result[i]["counter"] == "df.bytes.used.percent/fstype=xfs,mount=/data":
                    # print("data: ",falcon_result[i]["sum"]/1440)
                    data_xfs_used_1d = falcon_result[i]["sum"]/ (720 * point)
                    if data_xfs_used_1d < data_percentage:
                        data_flag = True
                    if data_xfs_used_1d != 0:
                        df_used_1d = data_xfs_used_1d
                if falcon_result[i]["counter"] == "df.bytes.used.percent/fstype=ext4,mount=/data":
                    # print("data: ",falcon_result[i]["sum"]/1440)
                    data_ext4_used_1d = falcon_result[i]["sum"]/ (720 * point)
                    if data_ext4_used_1d < data_percentage:
                        data_flag = True
                    if data_ext4_used_1d != 0:
                        df_used_1d = data_ext4_used_1d
            except Exception:
                continue
        # tmp: write to all
        # writeDataExcel(sheet_all, "all", ip, endpoint, cpu_busy, mem_used, data_used)

        # time.sleep(1)

        start_time_1w = 1623974400
        cpu_busy_1w_total = 0
        mem_used_1w_total = 0
        df_used_1w_total = 0
        for i in range(3):
            if i==0:
                start_time_1w += 0
            if i==1:
                start_time_1w += 86400
            if i==2:
                start_time_1w += 172800
            
            post_data_1w = {
                "start": start_time_1w,
                "end": start_time_1w + 43200,
                "cf": "AVERAGE",
                "endpoint_counters": [{
                    "endpoint": endpoint,
                    "counter": "cpu.idle"
                },{
                    "endpoint": endpoint,
                    "counter": "mem.memused.percent"
                },{
                    "endpoint": endpoint,
                    "counter": "df.bytes.used.percent/fstype=xfs,mount=/data"
                },{
                    "endpoint": endpoint,
                    "counter": "df.bytes.used.percent/fstype=ext4,mount=/data"
                }]
            }
            falcon_result = json.loads(postUrlContent(query_url, post_data_1w))
            # for i in range(3):
            try:
                # print(falcon_result[i])
                step = falcon_result[i]["step"]
                if step == 30:
                    point = 2
                else:
                    point = 1
                if falcon_result[i]["counter"] == "cpu.idle":
                    cpu_busy_1w = 100 - (falcon_result[i]["sum"]/(720 * point))
                    cpu_busy_1w_total += cpu_busy_1w
                if falcon_result[i]["counter"] == "mem.memused.percent":
                    mem_used_1w = falcon_result[i]["sum"]/(720 * point)
                    mem_used_1w_total += mem_used_1w
                if falcon_result[i]["counter"] == "df.bytes.used.percent/fstype=xfs,mount=/data":
                    data_xfs_used_1w = falcon_result[i]["sum"]/(720 * point)
                    if data_xfs_used_1w != 0:
                        df_used_1w = data_xfs_used_1w
                        df_used_1w_total += df_used_1w
                if falcon_result[i]["counter"] == "df.bytes.used.percent/fstype=ext4,mount=/data":
                    data_ext4_used_1w = falcon_result[i]["sum"]/(720 * point)
                    if data_ext4_used_1w != 0:
                        df_used_1w = data_ext4_used_1w
                        df_used_1w_total += df_used_1w
            except Exception:
                continue


        if cpu_flag and mem_flag and data_flag:
            print("endpoint: %s, cpu: %s, mem: %s, data: %s" % (endpoint, cpu_busy_1d, mem_used_1d, data_xfs_used_1d))
            if cpu_busy_1d == 0 and mem_used_1d == 0 and data_xfs_used_1d == 0:
                continue
            writeDataExcel(sheet_low, "low", ip, endpoint, abs(cpu_busy_1d), mem_used_1d, df_used_1d, abs(cpu_busy_1w_total/3), mem_used_1w_total/3, df_used_1w_total/3)

workbook = xlwt.Workbook()
sheet_all = createExcelAll(workbook)
sheet_low = createExcelLow(workbook)

main(sheet_all, sheet_low)
# writeDataExcel(sheet1)
saveExcel(workbook)
