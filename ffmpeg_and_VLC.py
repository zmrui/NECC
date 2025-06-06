import os
import time
import Mininet_testbed.analyze.mn_net_topo
import Mininet_testbed.analyze.fileanalyze
from matplotlib import pyplot as plt
import pandas as pd




def single_CC(cca2,rtt=50,bw=60,loss=0,flow=3,extra_prefix=""):
    
    # Single flow with loss condition

    # RoundTripTime in ms
    # BandWidth in Mbps

    # BandwidthDelayProduct in Bytes
    BDP = (bw * 1000 * rtt / 2 / 8)
    # Assume MSS is 1500
    maxqsize= int( BDP / 1500 )
    maxqsize = 1000
    print("maxqsize=",maxqsize)
    sub_folder_name = "ffmpeg/"+str(loss)+"loss"+extra_prefix

    mn_net = Mininet_testbed.analyze.mn_net_topo.mn_network(rtt=rtt,
                                    bw=bw,
                                    cca=cca2,
                                    reorderprobability=False,
                                    loss_probability=loss,
                                    maxqsize=maxqsize,
                                    sub_folder=sub_folder_name,
                                    nameprefix = "")
    
    mn_net.make_subfolder()
    mn_net.start_mininet()
    mn_net.disable_tso()

    input()
    for i in range(flow):
        mn_net.backgroundtraffic(duration_time=1200,bwlimit=25,port=6000+i)


    mn_net.start_ffmpeg_sender(inputfile='60stest.mp4',logname=f"cubic_flow{flow}_")
    input()

    mn_net.stop_mininet()

if __name__ == "__main__":
    single_CC('cubic_tshfd')