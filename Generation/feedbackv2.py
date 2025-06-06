from Generation.evaluate import *
import Generation.utils.util 
import Generation.utils.clients 
import Generation.utils.config 
import json
from datetime import datetime
import shutil, errno

def feedback_prompt(result_folder_path,cca,ccanewname,requirement,model,model_temperature,newusermessage,iteration,prompt_eng,skip=False):

    Generation.utils.util.mnclean()
    Generation.utils.util.remove_all_bpf_ccas()

    Generation.utils.util.deleteexistingcfile(result_folder_path,DELETE_EXISTING_C_FILE)
    print("Revision in {}".format(result_folder_path))
    if not os.path.exists(result_folder_path):
        print("{} not existed".format(result_folder_path))
        return False

    llm = Generation.utils.clients.LLM_CLIENT(model=model,result_folder=result_folder_path,temperature=model_temperature)
    llm.load_message_history(Generation.utils.config.PROMPT_DIR, Generation.utils.config.CCAFILEPATH[cca], requirement,pe=prompt_eng)
    llm.reload_system_message()
    if skip:
        return llm,ccanewname
    message_for_revise = copy.deepcopy(llm.message)
    last_assistant_response = message_for_revise.pop()
    for i in range(iteration-2):
        message_for_revise.pop()
        message_for_revise.pop()
    message_for_revise.append(last_assistant_response)
    if newusermessage is None: 
        message_for_revise.append({"role":"user",
                                "content":Generation.utils.config.revise_prompt_text_None})
        llm.append_message(role="user",content=Generation.utils.config.revise_prompt_text_None)
    else:
        message_for_revise.append({"role":"user",
                                "content":Generation.utils.config.revise_prompt_text.format(newusermessage)})
        llm.append_message(role="user",content=Generation.utils.config.revise_prompt_text.format(newusermessage))

    with open(os.path.join(os.getcwd(),llm.result_folder,"message_send_at_iteration{}.json".format(iteration)),"w") as f:
            json.dump(message_for_revise,f,indent=4)
    llm.send_revision_messages_no_save(message_for_revise)
    llm.save_last_assistant_result_to_message_history()
    llm.save_message_history()
    Generation.utils.util.save_message_of_iteration(result_folder_path,llm.latest_response_content,iteration)
    llm.refine_response()
    llm.change_cca_name(cca=cca, newname=ccanewname)
    llm.refine_c_code()
    llm.save_result_c_file(savename=ccanewname)
    Generation.utils.util.save_makefile(result_folder_path,ccanewname)
    return llm,ccanewname


def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else: raise

def test_current(processfolder,cca,ccanewname,iteration_count,timestr,feedback_level=5):
    Revise_message = []
    score = 0
    Iteration_details = []


        
# 1 Compile test
    Compile_errormessage = compile_check(cca,ccanewname,processfolder)
    citeration_item = {
        "NumofIt":iteration_count,
        "Type":"1-Compile",
        "Result":None,
        "FailedOn":None,
        "ErrorMessage":None
    }
    if Compile_errormessage:
        if feedback_level > 0:
            Revise_message.append(Compile_errormessage)
        citeration_item["ErrorMessage"] = str(Compile_errormessage)
        citeration_item['FailedOn'] = "Compile_Error"
        citeration_item['Result'] = False
        Iteration_details.append(citeration_item)
        return score, Iteration_details, Revise_message
    else:
        score += 1
        citeration_item['Result'] = True
        Iteration_details.append(citeration_item)

    # 2 BPF test
    BPF_errormessage = BPF_check(ccanewname,processfolder)
    biteration_item = {
        "NumofIt":iteration_count,
        "Type":"2-BPF",
        "Result":None,
        "FailedOn":None,
        "ErrorMessage":None
    }
    if BPF_errormessage:
        if feedback_level > 1:
            Revise_message.append(BPF_errormessage)
        biteration_item["ErrorMessage"] = str(BPF_errormessage)
        biteration_item['FailedOn'] = "BPF_Error"
        biteration_item['Result'] = False
        Iteration_details.append(biteration_item)
        return score, Iteration_details, Revise_message
    else:
        score += 1
        biteration_item['Result'] = True
        Iteration_details.append(biteration_item)

    # 3 Req test
    Red_check_result, Req_errormessage = User_Req_check(ccanewname,processfolder,timestr)
    riteration_item = {
        "NumofIt":iteration_count,
        "Type":"3-Requirement",
        "Result":None,
        "FailedOn":None,
        "ErrorMessage":None
    }
    if not Red_check_result:
        if feedback_level > 2:
            Revise_message.append(Req_errormessage)
        riteration_item["ErrorMessage"] = str(Req_errormessage)
        riteration_item['FailedOn'] = "Unsatisfied_User_Requirement"
        riteration_item['Result'] = False
        Iteration_details.append(riteration_item)
        # continue
    else:
        score += 0.5
        riteration_item['Result'] = True
        riteration_item["ErrorMessage"] = str(Req_errormessage)
        Iteration_details.append(riteration_item)
    # 3_2 Req test: short RTT
    Red_check_result, Req_errormessage = User_Req_check_short(ccanewname,processfolder,timestr)
    riteration_item = {
        "NumofIt":iteration_count,
        "Type":"3.2-Requirement_shortRTT",
        "Result":None,
        "FailedOn":None,
        "ErrorMessage":None
    }
    if not Red_check_result:
        if feedback_level > 2:
            Revise_message.append(Req_errormessage)
        riteration_item["ErrorMessage"] = str(Req_errormessage)
        riteration_item['FailedOn'] = "Unsatisfied_User_Requirement"
        riteration_item['Result'] = False
        Iteration_details.append(riteration_item)
        # continue
    else:
        score += 0.5
        riteration_item['Result'] = True
        riteration_item["ErrorMessage"] = str(Req_errormessage)
        Iteration_details.append(riteration_item)
    # 4 Safe1 test
    Safe1_result, Safe1_errormessage = safe1_check(ccanewname,processfolder,timestr)
    s1iteration_item = {
        "NumofIt":iteration_count,
        "Type":"4-Safety1",
        "Result":None,
        "FailedOn":None,
        "ErrorMessage":None
    }
    if not Safe1_result:
        if feedback_level > 3:
            Revise_message.append(Safe1_errormessage)
        s1iteration_item["ErrorMessage"] = str(Safe1_errormessage)
        s1iteration_item['FailedOn'] = "Safety1"
        s1iteration_item['Result'] = False
        Iteration_details.append(s1iteration_item)
        # continue
    else:
        score += 0.5
        s1iteration_item['Result'] = True
        s1iteration_item["ErrorMessage"] = str(Safe1_errormessage)
        Iteration_details.append(s1iteration_item)
    
    # 4-2 Safe1 test_short RTT
    Safe1_result, Safe1_errormessage = safe1_check_short(ccanewname,processfolder,timestr)
    s1iteration_item = {
        "NumofIt":iteration_count,
        "Type":"4.2-Safety1_shortRTT",
        "Result":None,
        "FailedOn":None,
        "ErrorMessage":None
    }
    if not Safe1_result:
        if feedback_level > 3:
            Revise_message.append(Safe1_errormessage)
        s1iteration_item["ErrorMessage"] = str(Safe1_errormessage)
        s1iteration_item['FailedOn'] = "Safety1"
        s1iteration_item['Result'] = False
        Iteration_details.append(s1iteration_item)
        # continue
    else:
        score += 0.5
        s1iteration_item['Result'] = True
        s1iteration_item["ErrorMessage"] = str(Safe1_errormessage)
        Iteration_details.append(s1iteration_item)

    # 5 Safe2 test
    Safe2_result, Safe2_errormessage = safe2_check(ccanewname,processfolder,timestr)
    s2iteration_item = {
        "NumofIt":iteration_count,
        "Type":"5-Safety2",
        "Result":None,
        "FailedOn":None,
        "ErrorMessage":None
    }
    if not Safe2_result:
        if feedback_level > 4:
            Revise_message.append(Safe2_errormessage)
        s2iteration_item["ErrorMessage"] = str(s2iteration_item["ErrorMessage"])+' and '+str(Safe2_errormessage)
        s2iteration_item['FailedOn'] = "Safety2"
        s2iteration_item['Result'] = False
        Iteration_details.append(s2iteration_item)
        # continue
    else:
        score += 0.5
        s2iteration_item['Result'] = True
        s2iteration_item["ErrorMessage"] = str(Safe2_errormessage)
        Iteration_details.append(s2iteration_item)
    
        # 5-2 Safe2 test_ shortRTT
    Safe2_result, Safe2_errormessage = safe2_check_short(ccanewname,processfolder,timestr)
    s2iteration_item = {
        "NumofIt":iteration_count,
        "Type":"5.2-Safety2_shortRTT",
        "Result":None,
        "FailedOn":None,
        "ErrorMessage":None
    }
    if not Safe2_result:
        if feedback_level > 4:
            Revise_message.append(Safe2_errormessage)
        s2iteration_item["ErrorMessage"] = str(s2iteration_item["ErrorMessage"])+' and '+str(Safe2_errormessage)
        s2iteration_item['FailedOn'] = "Safety2"
        s2iteration_item['Result'] = False
        Iteration_details.append(s2iteration_item)
        # continue
    else:
        score += 0.5
        s2iteration_item['Result'] = True
        s2iteration_item["ErrorMessage"] = str(Safe2_errormessage)
        Iteration_details.append(s2iteration_item)
    
    return score, Iteration_details, Revise_message

# NECC_report_template = {
#     "CCAName":None,
#     "Exception":False,
#     "UnexpectedError":None,
#     "CCAworkFolderPath":None,
#     "CCABase":None,
#     "LLMModel":None,
#     "Temperature":None,
#     "Requirement":None,
#     "FeedbackLevel":None,
#     'Score':None,
#     "IterationName":None,
#     "Evaluations":[],
#     "ReviseMessage": None
# }

def load_from_json_result(jsonconf,cnt=0):
    with open (jsonconf,'r')as f:
        jsonobj = json.load(f)
    try:
        item = jsonobj[cnt]
    except:
        item = None

    return item, jsonobj
