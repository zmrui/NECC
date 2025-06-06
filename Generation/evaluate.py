import Generation.utils.util 
import Generation.utils.clients 
import Generation.utils.config 
import Generation.utils.variable 
import Mininet_testbed.analyze
import Mininet_testbed.analyze.misc
import Mininet_testbed.req_check
import random
import subprocess
import os
import json
import copy
import sys

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
def load_message_only(timestr,cca,requirement,model,model_temperature,iteration,run,feedback_level,prompt_eng):
    Generation.utils.util.mnclean()
    Generation.utils.util.remove_all_bpf_ccas()
    result_folder_path = os.path.join(Generation.utils.config.REEVAL_DIR, cca + '-' + requirement + '-' + model + '-temp' + str(model_temperature)+ '-fb' + str(feedback_level)+ '-' + prompt_eng +"/run"+ str(run))
    print("Revision in {}".format(result_folder_path))

    llm = Generation.utils.clients.LLM_CLIENT(model=model,result_folder=result_folder_path,temperature=model_temperature)
    llm.load_message_history(Generation.utils.config.PROMPT_DIR, Generation.utils.config.CCAFILEPATH[cca], requirement,pe=prompt_eng)
    llm.reload_system_message()
    return llm

REGISTER_ENABLED = True
DELETE_EXISTING_C_FILE = False


def compile_check(cca,ccanewname,processfolder):
    make_command = ["make"]
    make_proc = subprocess.Popen(make_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=processfolder)
    stdout, stderr = make_proc.communicate()
    if make_proc.returncode == 0:
        print("Check#1 Make success to ", ccanewname+'.o')
        return None
    else:
        # Compile error
        stdoutstr = stdout.decode()
        stdout_err = stdoutstr[stdoutstr.index('error:'):stdoutstr.index('make:')].replace(ccanewname,cca+'.c')
        print('Check#1 Get make error:',stdout_err)
        return stdout_err
def BPF_check(ccanewname,processfolder):
    make_reg_command = ["make","register"]
    make_proc = subprocess.Popen(make_reg_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=processfolder)
    stdout, stderr = make_proc.communicate()
    if Generation.utils.util.check_cca_exist(ccanewname):
        print("Check#2 {} registered".format(ccanewname))
        return None
    else:
        # Compile error
        stdoutstr = stdout.decode()
        print('Check#2 Get register error:',stdoutstr)
        return stdoutstr
def User_Req_check(ccanewname,processfolder,timestr):
    bandwidth = int(Generation.utils.config.HOME_INTERNET_BW)
    delay_ms = 50
    loss = 0
    cca1, cca2= Mininet_testbed.analyze.misc.get_cca_name_pair(ccanewname)
    average_Mbps_new, average_Mbps_baseline = Mininet_testbed.req_check.Dumbell(n_flows=10,timestr=timestr,cca1=cca1,cca2=cca2,bw=bandwidth,delay=delay_ms,lossin=loss,ffpmeg=2)
    goodmessage = f'The modified version achieved User requirement, obtain {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network'
    badmessage = f'The modified version unfortunately does not achieve User requirement, obtain {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network. This performance need to increase to at least 12Mbps throughput'
    if average_Mbps_new < int(Generation.utils.config.REQ_BW):
        print('Check#3 ',badmessage)
        return       False, badmessage
    print('Check#3 ',goodmessage)
    return True, "Check#3"+ goodmessage
def User_Req_check_short(ccanewname,processfolder,timestr):
    bandwidth = int(Generation.utils.config.HOME_INTERNET_BW)
    delay_ms = 5
    loss = 0
    cca1, cca2= Mininet_testbed.analyze.misc.get_cca_name_pair(ccanewname)
    average_Mbps_new, average_Mbps_baseline = Mininet_testbed.req_check.Dumbell(n_flows=10,timestr=timestr,cca1=cca1,cca2=cca2,bw=bandwidth,delay=delay_ms,lossin=loss,ffpmeg=2)
    goodmessage = f'The modified version achieved User requirement, obtain {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network'
    badmessage = f'The modified version unfortunately does not achieve User requirement, obtain {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network. This performance need to increase to at least 12Mbps throughput'
    if average_Mbps_new < int(Generation.utils.config.REQ_BW):
        print('Check#3-2 ',badmessage)
        return       False, badmessage
    print('Check#3-2 ',goodmessage)
    return True, "Check#3-2"+ goodmessage
def safe1_check(ccanewname,processfolder,timestr):
    systemcca('cubic')
    bandwidth = int(Generation.utils.config.HOME_INTERNET_BW)
    delay_ms = 50
    loss = 0
    cca1, cca2= Mininet_testbed.analyze.misc.get_cca_name_pair(ccanewname)
    average_Mbps_new, average_Mbps_baseline = Mininet_testbed.req_check.Dumbell(n_flows=1,timestr=timestr,cca1=cca1,cca2=cca2,bw=bandwidth,delay=delay_ms,lossin=loss,ffpmeg=0)
    goodmessage = f'The modified version obtain {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network'
    badmessage = f'The modified version unfortunately exceed allowed 31 Mbps throughput, reaching {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay network. This performance needs to be reduced to comply with the 31Mbps limit.'
    badmessage2 = f'The modified version unfortunately does not achieve User requirement, obtain {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network. This performance need to increase to at least 12Mbps throughput'
    if average_Mbps_new > int(Generation.utils.config.REQ_BW):
        if average_Mbps_new > int(Generation.utils.config.HOME_BW_LIMIT):
            print('Check#4 ',badmessage)
            return       False, badmessage
        else:
            print('Check#4 ',goodmessage)
            return True, "Check#4"+ goodmessage
    print('Check#4 ',badmessage2)
    return       False, badmessage2
def safe1_check_short(ccanewname,processfolder,timestr):
    systemcca('cubic')
    bandwidth = int(Generation.utils.config.HOME_INTERNET_BW)
    delay_ms = 5
    loss = 0
    cca1, cca2= Mininet_testbed.analyze.misc.get_cca_name_pair(ccanewname)
    average_Mbps_new, average_Mbps_baseline = Mininet_testbed.req_check.Dumbell(n_flows=1,timestr=timestr,cca1=cca1,cca2=cca2,bw=bandwidth,delay=delay_ms,lossin=loss,ffpmeg=0)
    goodmessage = f'The modified version obtain {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network'
    badmessage = f'The modified version unfortunately exceed allowed 31 Mbps throughput, reaching {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay network. This performance needs to be reduced to comply with the 31Mbps limit.'
    badmessage2 = f'The modified version unfortunately does not achieve User requirement, obtain {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network. This performance need to increase to at least 12Mbps throughput'
    if average_Mbps_new > int(Generation.utils.config.REQ_BW):
        if average_Mbps_new > int(Generation.utils.config.HOME_BW_LIMIT):
            print('Check#4-2 ',badmessage)
            return       False, badmessage
        else:
            print('Check#4-2 ',goodmessage)
            return True, "Check#4-2"+ goodmessage
    print('Check#4-2 ',badmessage2)
    return       False, badmessage2
def safe2_check(ccanewname,processfolder,timestr):
    bandwidth = int(Generation.utils.config.HOME_INTERNET_BW)
    delay_ms = 50
    loss = 8
    cca1, cca2= Mininet_testbed.analyze.misc.get_cca_name_pair(ccanewname)
    average_Mbps_new, average_Mbps_baseline = Mininet_testbed.req_check.Dumbell(n_flows=2,timestr=timestr,cca1=cca1,cca2=cca2,bw=bandwidth,delay=delay_ms,lossin=loss,ffpmeg=0)
    goodmessage = f'The modified version obtain {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network'
    badmessage = f'The modified version unfortunately does not reduce the throughpt as original logic, reaching {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network. This performance needs to be reduced as original logic when loss rate is greater than 5%.'
    if abs(average_Mbps_new-average_Mbps_baseline)>2:
        print('Check#5 ',badmessage)
        return       False, badmessage
    print('Check#5 ',goodmessage)
    return True, "Check#5"+ goodmessage
def safe2_check_short(ccanewname,processfolder,timestr):
    bandwidth = int(Generation.utils.config.HOME_INTERNET_BW)
    delay_ms = 5
    loss = 8
    cca1, cca2= Mininet_testbed.analyze.misc.get_cca_name_pair(ccanewname)
    average_Mbps_new, average_Mbps_baseline = Mininet_testbed.req_check.Dumbell(n_flows=2,timestr=timestr,cca1=cca1,cca2=cca2,bw=bandwidth,delay=delay_ms,lossin=loss,ffpmeg=0)
    goodmessage = f'The modified version obtain {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network'
    badmessage = f'The modified version unfortunately does not reduce the throughpt as original logic, reaching {average_Mbps_new} Mbps average thrgouhput in a {bandwidth}Mbps {delay_ms}ms delay {loss}% loss network. This performance needs to be reduced as original logic when loss rate is greater than 5%.'
    if abs(average_Mbps_new-average_Mbps_baseline)>2:
        print('Check#5-2 ',badmessage)
        return       False, badmessage
    print('Check#5-2 ',goodmessage)
    return True, "Check#5-2"+ goodmessage

def test_current(processfolder,cca,ccanewname,iteration_count,timestr,feedback_level=5,skip=False):
    Revise_message = []
    score = -1
    Iteration_details = []
    if skip:
        return score, Iteration_details, Revise_message

# 1 Compile test
    Compile_errormessage = compile_check(cca,ccanewname,processfolder)
    citeration_item = copy.deepcopy(Generation.utils.config.Evaluation_item_template)
    citeration_item["EvaluationItemName"] = "1-Compile"
    if Compile_errormessage:
        if feedback_level > 0:
            Revise_message.append(Compile_errormessage)
        citeration_item["Message"] = str(Compile_errormessage)
        citeration_item['FailReason'] = "Compile_Error"
        citeration_item['Result'] = False
        Iteration_details.append(citeration_item)
        return score, Iteration_details, Revise_message
    else:
        score += 1
        citeration_item['Result'] = True
        Iteration_details.append(citeration_item)

    # 2 BPF test
    BPF_errormessage = BPF_check(ccanewname,processfolder)
    biteration_item = copy.deepcopy(Generation.utils.config.Evaluation_item_template)
    biteration_item["EvaluationItemName"] = "2-BPF"
    if BPF_errormessage:
        if feedback_level > 1:
            Revise_message.append(BPF_errormessage)
        biteration_item["Message"] = str(BPF_errormessage)
        biteration_item['FailReason'] = "BPF_Error"
        biteration_item['Result'] = False
        Iteration_details.append(biteration_item)
        return score, Iteration_details, Revise_message
    else:
        score += 1
        biteration_item['Result'] = True
        Iteration_details.append(biteration_item)

    # 3 Req test
    Red_check_result, Req_errormessage = User_Req_check(ccanewname,processfolder,timestr)
    riteration_item = copy.deepcopy(Generation.utils.config.Evaluation_item_template)
    riteration_item["EvaluationItemName"] = "3-Requirement"

    if not Red_check_result:
        if feedback_level > 2:
            Revise_message.append(Req_errormessage)
        riteration_item["Message"] = str(Req_errormessage)
        riteration_item['FailReason'] = "Unsatisfied_User_Requirement"
        riteration_item['Result'] = False
        Iteration_details.append(riteration_item)
        # continue
    else:
        score += 0.5
        riteration_item['Result'] = True
        riteration_item["Message"] = str(Req_errormessage)
        Iteration_details.append(riteration_item)

    # 3_2 Req test: short RTT
    Red_check_result, Req_errormessage = User_Req_check_short(ccanewname,processfolder,timestr)
    riteration_item = copy.deepcopy(Generation.utils.config.Evaluation_item_template)
    riteration_item["EvaluationItemName"] = "3.2-Requirement_shortRTT"
    if not Red_check_result:
        if feedback_level > 2:
            Revise_message.append(Req_errormessage)
        riteration_item["Message"] = str(Req_errormessage)
        riteration_item['FailReason'] = "Unsatisfied_User_Requirement"
        riteration_item['Result'] = False
        Iteration_details.append(riteration_item)
        # continue
    else:
        score += 0.5
        riteration_item['Result'] = True
        riteration_item["Message"] = str(Req_errormessage)
        Iteration_details.append(riteration_item)

    # 4 Safe1 test
    Safe1_result, Safe1_errormessage = safe1_check(ccanewname,processfolder,timestr)
    s1iteration_item = copy.deepcopy(Generation.utils.config.Evaluation_item_template)
    s1iteration_item["EvaluationItemName"] = "4-Safety1"

    if not Safe1_result:
        if feedback_level > 3:
            Revise_message.append(Safe1_errormessage)
        s1iteration_item["Message"] = str(Safe1_errormessage)
        s1iteration_item['FailReason'] = "Exceed_maximum_throughput"
        s1iteration_item['Result'] = False
        Iteration_details.append(s1iteration_item)
        # continue
    else:
        score += 0.5
        s1iteration_item['Result'] = True
        s1iteration_item["Message"] = str(Safe1_errormessage)
        Iteration_details.append(s1iteration_item)
    
    # 4-2 Safe1 test_short RTT
    Safe1_result, Safe1_errormessage = safe1_check_short(ccanewname,processfolder,timestr)
    s1iteration_item = copy.deepcopy(Generation.utils.config.Evaluation_item_template)
    s1iteration_item["EvaluationItemName"] = "4.2-Safety1_shortRTT"

    if not Safe1_result:
        if feedback_level > 3:
            Revise_message.append(Safe1_errormessage)
        s1iteration_item["Message"] = str(Safe1_errormessage)
        s1iteration_item['FailReason'] = "Exceed_maximum_throughput"
        s1iteration_item['Result'] = False
        Iteration_details.append(s1iteration_item)
        # continue
    else:
        score += 0.5
        s1iteration_item['Result'] = True
        s1iteration_item["Message"] = str(Safe1_errormessage)
        Iteration_details.append(s1iteration_item)

    # 5 Safe2 test
    Safe2_result, Safe2_errormessage = safe2_check(ccanewname,processfolder,timestr)
    s2iteration_item = copy.deepcopy(Generation.utils.config.Evaluation_item_template)
    s1iteration_item["EvaluationItemName"] = "5-Safety2"

    if not Safe2_result:
        if feedback_level > 4:
            Revise_message.append(Safe2_errormessage)
        s2iteration_item["Message"] = str(Safe2_errormessage)
        s2iteration_item['FailReason'] = "Not_drop_throughput_during_congestion"
        s2iteration_item['Result'] = False
        Iteration_details.append(s2iteration_item)
        # continue
    else:
        score += 0.5
        s2iteration_item['Result'] = True
        s2iteration_item["Message"] = str(Safe2_errormessage)
        Iteration_details.append(s2iteration_item)
    
        # 5-2 Safe2 test_ shortRTT
    Safe2_result, Safe2_errormessage = safe2_check_short(ccanewname,processfolder,timestr)
    s2iteration_item = copy.deepcopy(Generation.utils.config.Evaluation_item_template)
    s1iteration_item["EvaluationItemName"] = "5.2-Safety2_shortRTT"

    if not Safe2_result:
        if feedback_level > 4:
            Revise_message.append(Safe2_errormessage)
        s2iteration_item["Message"] = str(Safe2_errormessage)
        s2iteration_item['FailReason'] = "Not_drop_throughput_during_congestion"
        s2iteration_item['Result'] = False
        Iteration_details.append(s2iteration_item)
        # continue
    else:
        score += 0.5
        s2iteration_item['Result'] = True
        s2iteration_item["Message"] = str(Safe2_errormessage)
        Iteration_details.append(s2iteration_item)
    
    return score, Iteration_details, Revise_message