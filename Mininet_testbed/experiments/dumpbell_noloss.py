import os
import sys
import subprocess

script_dir = os.path.dirname( __file__ )
mymodule_dir = os.path.join( script_dir, '..')
sys.path.append( mymodule_dir )

from Mininet_testbed.core.topologies import *
from mininet.net import Mininet
from Mininet_testbed.core.analysis import *
import json
from Mininet_testbed.core.utils import *
from Mininet_testbed.core.emulation import *
# from core.config import *

def systemcca(cca:str):
    writecmd = f"sudo sysctl -w net.ipv4.tcp_congestion_control={cca}"
    checkcmd = "sudo sysctl net.ipv4.tcp_congestion_control"
    os.system(writecmd)
    

    result = subprocess.run(["sudo", "sysctl","net.ipv4.tcp_congestion_control"], capture_output=True, text=True)
    res = result.stdout
    # res = os.system(checkcmd)
    if cca in res:
        return True
    else:
        return False


def run_emulation(ffpmeg, timestr,topology, protocol, params, bw, delay, qmult, HOME_DIR, tcp_buffer_mult=3, run=0, aqm='fifo', loss=None, n_flows=2,CCA1='cubic',CCA2='cubic',CCA3='cubic'):
    if topology == 'Dumbell':
        topo = DumbellTopo(**params)
    else:
        print("ERROR: topology \'%s\' not recognised" % topology)

    bdp_in_bytes = int(bw * (2 ** 20) * 2 * delay * (10 ** -3) / 8)
    qsize_in_bytes = max(int(qmult * bdp_in_bytes), 1500)

    duration = int((2*delay))

    
    net = Mininet(topo=topo)
    path = "%s/FastDumbell/%s-%s/%s_%s_%smbit_%sms_%spkts_%sloss_%sflows_%stcpbuf_%s/run%s" % (HOME_DIR, timestr,protocol, aqm, topology, bw, delay, int(qsize_in_bytes/1500), loss, n_flows, tcp_buffer_mult, protocol, run)
    mkdirp(path)
    subprocess.call(['chown', '-R' ,'$USER', path])




    #  Configure size of TCP buffers
    #  TODO: check if this call can be put after starting mininet
    #  TCP buffers should account for QSIZE as well
    # tcp_buffers_setup(bdp_in_bytes + qsize_in_bytes, multiplier=tcp_buffer_mult)
    

    net.start()

    if ffpmeg == 1:
        if not systemcca(protocol):
            raise RuntimeError(f"Config {protocol} Fail")

    disable_offload(net)

    network_config = [NetworkConf('s1', 's2', None, 2*delay, 3*bdp_in_bytes, False, 'fifo', loss),
                      NetworkConf('s2', 's3', bw, None, qsize_in_bytes, False, aqm, None)]
    
    if n_flows == 1:
        traffic_config = [TrafficConf('c1', 'x1', 0, 30, protocol)]
                        #   TrafficConf('c2', 'x2', 25, 75, protocol),
                        #   TrafficConf('c3', 'x3', 50, 50, protocol),
                        #   TrafficConf('c4', 'x4', 75, 25, protocol)]
    elif n_flows == 2:
        traffic_config = [TrafficConf('c1', 'x1', 0, 30, protocol),
                           TrafficConf('c2', 'x2', 0, 30, CCA1)]
        # traffic_config = [TrafficConf('c1', 'x1', 0, 2*duration, CCA1),
        #                    TrafficConf('c2', 'x2', 0, 2*duration, protocol)]
    elif n_flows == 3:
        # traffic_config = [TrafficConf('c1', 'x1', 0, 150, protocol),
        #                  TrafficConf('c2', 'x2', 25, 125, CCA1),
        #                  TrafficConf('c3', 'x3', 50, 150, CCA2)]
        traffic_config = [TrafficConf('c1', 'x1', 0, 30, protocol),
                         TrafficConf('c2', 'x2', 0, 30, CCA1),
                         TrafficConf('c3', 'x3', 0, 30, CCA2)]
    elif n_flows == 4:
        traffic_config = [TrafficConf('c1', 'x1', 0, 30,  protocol),
                         TrafficConf('c2', 'x2', 0, 30, CCA1),
                         TrafficConf('c3', 'x3', 0, 30, CCA2),
                         TrafficConf('c4', 'x4', 0, 30, CCA2)]
    elif n_flows == 10:
        traffic_config = [TrafficConf('c1', 'x1', 0, 30,  protocol),
                         TrafficConf('c2', 'x2', 0, 30, CCA1),
                         TrafficConf('c3', 'x3', 0, 30, CCA2),
                         TrafficConf('c4', 'x4', 0, 30, CCA2),
                         TrafficConf('c5', 'x5', 0, 30, CCA2),
                         TrafficConf('c6', 'x6', 0, 30, CCA2),
                         TrafficConf('c7', 'x7', 0, 30, CCA2),
                         TrafficConf('c8', 'x8', 0, 30, CCA2),
                         TrafficConf('c9', 'x9', 0, 30, CCA2),
                         TrafficConf('c10', 'x10', 0, 30, CCA2)]


    
    em = Emulation(net, network_config, traffic_config, path)

    em.configure_network()
    em.configure_traffic()
    em.ff=ffpmeg
    em.run()
    em.run_countinued()
    em.dump_info()
    net.stop()

    change_all_user_permissions(path)

    # Process raw outputs into csv files
    process_raw_outputs(path,ff=ffpmeg)

    return path

if __name__ == '__main__':

    topology = 'Dumbell'
    
    delay = int(sys.argv[1])
    bw = int(sys.argv[2])
    qmult = float(sys.argv[3])
    protocol = sys.argv[4]
    run = int(sys.argv[5])
    aqm = sys.argv[6]
    loss = sys.argv[7]
    n_flows = int(sys.argv[8])
    params = {'n':n_flows}

    # Same sysctl as original Orca
    # os.system('sudo sysctl -w net.ipv4.tcp_wmem="4096 32768 4194304"')
    os.system('sudo sysctl -w net.ipv4.tcp_low_latency=1')
    os.system('sudo sysctl -w net.ipv4.tcp_autocorking=0')
    os.system('sudo sysctl -w net.ipv4.tcp_no_metrics_save=1')
    # os.system('sudo sysctl -w fs.inotify.max_user_watches=524288')
    # os.system('sudo sysctl -w fs.inotify.max_user_instances=524288')

    print('Loss is %s' % loss)
    run_emulation(topology, protocol, params, bw, delay, qmult, 22, run, aqm, loss, n_flows) #Qsize should be at least 1 MSS.

    # Plot results
    # plot_results(path)