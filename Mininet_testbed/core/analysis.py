import json
from core.parsers import *
from core.utils import *
import pandas as pd
    
def process_raw_outputs(path,ff):
    with open(path + '/emulation_info.json', 'r') as fin:
        emulation_info = json.load(fin)

    flows = emulation_info['flows']
    flows = list(filter(lambda flow: flow[5] != 'netem' and flow[5] != 'tbf', flows))
    flows.sort(key=lambda x: x[-2])

    csv_path = path + "/csvs"
    mkdirp(csv_path)
    change_all_user_permissions(path)
    for flow in flows:
        sender = str(flow[0])
        receiver = str(flow[1])
        sender_ip = str(flow[2])
        receiver_ip = str(flow[3])
        start_time = int(flow[-3])

        # if flow[-2] == 'cubic':
        if CC_in_kernel(flow[-2]):
            port=5201

            # Convert sender output into csv
            if ff==1 and (sender == 'x1' or sender == 'c1'):
                senderdf = parse_ffmpeg(path+"/%s_output.txt" % sender)
            else:
                senderdf = parse_iperf_json(path+"/%s_output.txt" % sender, start_time)
            senderdf.to_csv("%s/%s.csv" % (csv_path,sender), index=False)

            # Convert receiver output into csv
            if ff==1 and (sender == 'x1' or sender == 'c1'):
                receiverdf = parse_ffmpeg(path+"/%s_output.txt" % receiver)
            else:
                receiverdf = parse_iperf_json(path+"/%s_output.txt" % receiver, start_time)
            
            receiverdf.to_csv("%s/%s.csv" % (csv_path, receiver), index=False)
            # Comments for no tcp_probe
            # receiver_probe_df = parse_tcp_probe_output(path + "/tcp_probe.txt", '%s:%s' % (receiver_ip, port), key='destination')
            # receiver_probe_df.to_csv("%s/%s_probe.csv" % (csv_path, sender),index=False)
    
        elif flow[-2] == 'orca':
            return
            port=4444
            # Convert sender output into csv
            df = parse_orca_output(path+"/%s_output.txt" % sender, start_time)
            df.to_csv("%s/%s.csv" %  (csv_path, sender), index=False)

            # Convert receiver output into csv
            df = parse_orca_output(path+"/%s_output.txt" % receiver, start_time)
            df.to_csv("%s/%s.csv" %  (csv_path, receiver),index=False)


            probe_df = parse_tcp_probe_output(path + "/tcp_probe.txt", '%s:%s' % (sender_ip, port),  key='source')
            probe_df.to_csv("%s/%s_probe.csv" % (csv_path, sender),index=False)

        elif flow[-2] == 'aurora':
            return
            # Convert sender output into csv
            df = parse_aurora_output(path+"/%s_output.txt" % sender, start_time)
            df.to_csv("%s/%s.csv" %  (csv_path, sender), index=False)

            # Convert receiver output into csv
            df = parse_aurora_output(path+"/%s_output.txt" % receiver, start_time)
            df.to_csv("%s/%s.csv" %  (csv_path, receiver),index=False)
        
        else:
            print("Unknow CCA")
