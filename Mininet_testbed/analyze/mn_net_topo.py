from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import os
import time
from decimal import *
import Mininet_testbed.analyze.fileanalyze
import time

INPUTFILE = '~/input.mp4'

class ReorderLossTopo( Topo ):
    def build( self, rtt, bw, reorderprobability, lossprob, correlation,reorder_distance,maxq):

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')

        if reorderprobability:
            reorder_string="reorder %f%%%% %d%%%%"%(reorderprobability, correlation)
        else:
            reorder_string=None
        if reorder_distance:
            lnkdelay = reorder_distance
        else:
            lnkdelay = 1

        self.addLink(h1,h3,
                   delay='%dms'%(lnkdelay), jitter=reorder_string, loss=lossprob)
        self.addLink(h2,h3,
                   bw=bw, delay='%dms'%(rtt//2),loss=0,max_queue_size=maxq)


#start_mininet
#Finished
#set rtt, bandwidth, congestion control algorithm
class mn_network:
    def __init__(self,rtt=int,
                 bw=int,
                 cca=str,
                 maxqsize=int,
                 sub_folder=None,
                 loss_probability=None,
                 reorderprobability=None,
                 correlation=None,
                 reorder_distance=None,
                 nameprefix="") -> None:
        
        self.rtt=rtt
        self.bw=bw
        self.cca=cca
        self.reorder=reorderprobability
        self.reorder_tc_prob = None

        self.probability=reorderprobability
        # 25 == 25% delay
        
        if self.probability:
            self.reorder_tc_prob = 100.0 - self.probability
        # 25 == 25% send immedtly and 75% delay

        self.correlation=correlation
        self.reorder_distance=reorder_distance
        self.packet_drop_position_list=None
        self.packet_reorder_position_list=None
        self.maxqsize=maxqsize
        self.loss_probability = loss_probability
        self.name=nameprefix+cca+"_"+str(rtt)+"ms_"+str(bw)+"Mbps"
        self.top_folder=os.getcwd()
        self.sub_folder=None
        if sub_folder:
            self.sub_folder= os.path.join(self.top_folder,sub_folder) 


        self.iperf_start_time = None
        self.iperf_expected_end_time = None

        self.CWND_start = 90
        self.tso_enabled = True

        FILE_PATH = "/proc/kmsg"
        self.kmsg_file = open(FILE_PATH,"r")
        print("@","rtt="+str(rtt)+"ms","bw="+str(bw)+"Mbps","cca="+cca)
        self.startTime = time.time()

        self.focus_begin = 0
        self.focus_end = 0
    def get_name(self):
        return self.name
    def make_subfolder(self):
        if self.sub_folder:
            if not os.path.exists(self.sub_folder):
                os.makedirs(self.sub_folder)
        
        self.workingdir = os.path.join(os.getcwd(),self.sub_folder)
        print("Working Dir:",self.workingdir) 
            
    def start_mininet(self):

        topo = ReorderLossTopo(rtt=self.rtt,
                               bw=self.bw, 
                               lossprob=self.loss_probability, 
                               reorderprobability = self.reorder_tc_prob,
                               correlation=self.correlation,
                               reorder_distance = self.reorder_distance, 
                               maxq = self.maxqsize)
        net = Mininet( topo=topo,
                    host=CPULimitedHost, link=TCLink, xterms=True,
                    autoStaticArp=True )    

        net.start()
        h1, h2, h3 = net.getNodeByName('h1', 'h2', 'h3')

        h1eth0 = h1.intf("h1-eth0")
        h1eth0.setIP("192.168.0.1/24")
        h1.cmd("route add -net 10.0.0.0/24 dev h1-eth0 gw 192.168.0.3")

        h2eth0 = h2.intf("h2-eth0")
        h2eth0.setIP("10.0.0.2/24")
        h2.cmd("route add -net 192.168.0.0/24 dev h2-eth0 gw 10.0.0.3")


        h3eth0 = h3.intf("h3-eth0")
        h3eth0.setIP("192.168.0.3/24")
        h3eth1 = h3.intf("h3-eth1")
        h3eth1.setIP("10.0.0.3/24")

        # if not "bpf" in self.cca:
        #     h1.cmd("sysctl -w net.ipv4.tcp_congestion_control=%s"%(self.cca))
        h1.cmd("sysctl -p")
        h3.cmd("sysctl -p")
        
        print("@ start mininet: %s"%(time.time()-self.startTime))
        self.net=net
        self.h1=h1
        self.h2=h2
        self.h3=h3
        return net,h1,h2,h3

    def stop_mininet(self):
        print("@ stop mininet")
        with open(os.path.join(self.workingdir,self.name+'_name.txt'),'w') as f:
            f.write(self.name)
        self.net.stop()

    def start_iperf_time_json(self,duration_time:int, port=5201):
        self.duration_time = duration_time + 1
        # time.sleep(2)
        # os.system("dmesg -c > /dev/null")
        self.iperflogpath = os.path.join(self.workingdir,self.name+"_iperflog")
        self.receiver_iperflogpath = os.path.join(self.workingdir,self.name+"_iperflog_receiver")
        if os.path.isfile(self.iperflogpath):
            os.remove(self.iperflogpath)
        if os.path.isfile(self.receiver_iperflogpath):
            os.remove(self.receiver_iperflogpath)
        self.h2.cmd("iperf3 -s -p %d -i 1 --json --logfile %s -1 &"%(port,self.receiver_iperflogpath))
        h1cmd="iperf3 -c 10.0.0.2 -p %d --congestion %s -t %d -f m -i 1 --json --logfile %s &"%(port,self.cca,duration_time,self.iperflogpath)
        self.h1.cmd(h1cmd)
        print('[h1]:',h1cmd)
        self.iperf_start_time = time.time()
        self.iperf_expected_end_time = self.iperf_start_time + self.duration_time
        print("@ iperf started for %d seconds :%s"%(duration_time,time.time()-self.startTime))
        return "10.0.0.2:5201"
    def backgroundtraffic(self,duration_time:int, bwlimit, port=5201):
        self.h2.cmd(f"iperf3 -s -p {port} -i 1 -1 &")
        h1cmd=f"iperf3 -c 10.0.0.2 -p {port} --congestion 'cubic' -b {bwlimit}M -t {duration_time} > iperflog{port}.txt &"
        self.h1.cmd(h1cmd)
        print('[h1]:',h1cmd)

    def start_ffmpeg_sender(self,logname,inputfile='gamerec.mp4',senderip='192.168.0.1',receiverip='10.0.0.2'):
        # ffcmd = f"ffmpeg -re -i {inputfile} -c copy -stats_period 1 -f flv tcp://{senderip}:5201?listen > fflog1.txt 2>&1 &"
        # ffcmd = f"ffmpeg -re -i {inputfile}  -stats_period 1 -f rtsp -rtsp_transport tcp listen rtsp://{senderip}:5201/live.sdp > fflog1.txt 2>&1 &"
        ffcmd = f"ffmpeg -re -i {inputfile} -c copy -listen 1 -stats_period 1 -f flv rtmp://{senderip}:5201/live/app > SSIM/{logname}fflog1.txt 2>&1 &"
        # ffcmd = f"ffmpeg -re -i {inputfile} -c copy -listen 1 -stats_period 1 -f flv rtmp://127.0.0.1:5200/live/app1 > SSIM/{logname}fflog1.txt 2>&1 &"
        print(self.h1.cmd(ffcmd))
        # time.sleep(1)
        # ffcmd = f"ffmpeg -i rtmp://127.0.0.1:5200/live/app1 -c copy -listen 1 -stats_period 1 -f flv rtmp://{senderip}:5201/live/app > SSIM/{logname}fflog2.txt 2>&1 &"
        # print(self.h1.cmd(ffcmd))
        pass

    def start_ffmpeg_reveiver(self,receivepath, senderip='192.168.0.1',receiverip='10.0.0.2'):
        if os.path.exists(f'{receivepath}/output.mp4'):
            os.remove(f'{receivepath}/output.mp4')
        # ffcmd = f"ffmpeg -i tcp://{senderip}:5201 -tune zerolatency {receivepath}/output.mp4"
        # ffcmd = f"ffplay -fflags nobuffer -max_delay 1 -autoexit -tune zerolatency -i tcp://{senderip}:5201"
        # ffcmd = f"ffplay -autoexit -i tcp://{senderip}:5201"
        # ffcmd = f"ffmpeg -i tcp://{senderip}:5201 {receivepath}/output.mp4"
        # ffcmd = f'ffplay -i rtmp://{senderip}:5201/live/app'
        ffcmd = f'ffmpeg -i rtmp://{senderip}:5201/live/app -c copy {receivepath}'
        # print(ffcmd)
        print(self.h2.cmd(ffcmd))
        pass
        
    def disable_tso(self):
        self.tso_enabled = False
        print(self.h1.cmd("ethtool -K h1-eth0 tx off sg off tso off gso off"),end='')
        print(self.h2.cmd("ethtool -K h2-eth0 tx off sg off tso off gso off"),end='')
        print(self.h3.cmd("ethtool -K h3-eth0 tx off sg off tso off gso off"),end='')
        print(self.h3.cmd("ethtool -K h3-eth1 tx off sg off tso off gso off"),end='')
        # print(self.h3.cmd("wireshark &"))
        
