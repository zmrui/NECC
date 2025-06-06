import os
import time
import Mininet_testbed.analyze
# from matplotlib import pyplot as plt
import pandas as pd

import Mininet_testbed.experiments.dumpbell_noloss
import Mininet_testbed.analyze.fileanalyze
import Generation.utils.config

def Dumbell(timestr,cca1,cca2,n_flows,delay,bw,ffpmeg=2,lossin=None):
    if lossin == 0:
        loss = None
    else:
        loss = lossin
    path1 = Mininet_testbed.experiments.dumpbell_noloss.run_emulation(
        topology='Dumbell',
        protocol=cca1,
        params={'n':n_flows},
        delay=delay,
        bw=bw,
        qmult=1, 
        tcp_buffer_mult=3, 
        run=0, 
        aqm='fifo', 
        loss=loss, 
        n_flows=n_flows,
        CCA1=cca2,
        HOME_DIR=Generation.utils.config.RUNLOG_DIR,
        timestr=timestr,
        ffpmeg=ffpmeg
    )
    
    x1average_Mbps, x2average_Mbps = Mininet_testbed.analyze.fileanalyze.parse_two_average_throughput(path1)

    return round(x1average_Mbps,2), round(x2average_Mbps,2)