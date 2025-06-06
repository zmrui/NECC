import os
import subprocess
def check_cca_exist(ccaname):
    check_command = ["sysctl","net.ipv4.tcp_available_congestion_control"]
    make_proc = subprocess.Popen(check_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = make_proc.communicate()
    stdoutstr = stdout.decode()
    if ccaname in stdoutstr:
        return True
    else:
        return False


#     return cca_name_list
def get_cca_name_pair(newccaname):
    cca1 = newccaname
    cca2 = None
    if 'reno' in newccaname:
        cca2 = 'reno'
    elif 'cubic' in newccaname:
        cca2 = 'cubic'
    elif 'illinois' in newccaname:
        cca2 = 'illinois'
    elif 'vegas' in newccaname:
        cca2 = 'vegas'
    return cca1, cca2