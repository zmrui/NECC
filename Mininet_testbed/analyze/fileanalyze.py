from matplotlib import pyplot as plt
from decimal import Decimal
import os
import csv
import pandas as pd
import json


def parse_ffmpeg(path:str):
    segs = path.split("_")
    for seg in segs:
        if 'mbit' in seg:
            bw = int(seg.replace("mbit",''))
            break
    csv_path = path + "/csvs"
    
    sendercsv = csv_path + '/c1.csv'
   
    df = pd.read_csv(sendercsv)

    totalkBytes = Decimal(df.iloc[-1]['Total_kBytes'])
    totalkbits = totalkBytes * 8
    totalMbits = totalkbits / 1000
    averageMbps = totalMbits/len(df)
    

    return averageMbps

def parse_x2_average_throughput(path:str):
    
    receiver2_iperf_file = path + "/x2_output.txt"

    if os.path.exists(receiver2_iperf_file):
        with open(receiver2_iperf_file, 'r') as fin:
            iperfOutput2 = json.load(fin)
            average_bps2 = Decimal(iperfOutput2['end']['sum_received']['bits_per_second'])
            x2average_Mbps = average_bps2/1000000
    else:
        x2average_Mbps = 0

    return  x2average_Mbps

def parse_two_average_throughput(path:str):
    segs = path.split("_")
    for seg in segs:
        if 'mbit' in seg:
            bw = int(seg.replace("mbit",''))
            break
    csv_path = path + "/csvs"
    
    receiver1_iperf_file = path + "/x1_output.txt"
    receiver2_iperf_file = path + "/x2_output.txt"

    with open(receiver1_iperf_file, 'r') as fin:
        iperfOutput1 = json.load(fin)
        average_bps1 = Decimal(iperfOutput1['end']['sum_received']['bits_per_second'])
        x1average_Mbps = average_bps1/1000000

    if os.path.exists(receiver2_iperf_file):
        with open(receiver2_iperf_file, 'r') as fin:
            iperfOutput2 = json.load(fin)
            average_bps2 = Decimal(iperfOutput2['end']['sum_received']['bits_per_second'])
            x2average_Mbps = average_bps2/1000000
    else:
        x2average_Mbps = 0

    return x1average_Mbps, x2average_Mbps