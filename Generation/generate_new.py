import Generation.utils.util 
import Generation.evaluate
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

REGISTER_ENABLED = True
DELETE_EXISTING_C_FILE = False

def initial_prompt(timestr,cca,requirement,model,model_temperature,iteration,run,feedback_level,prompt_eng):
    Generation.utils.util.mnclean()
    result_folder_path = os.path.join(Generation.utils.config.RESULTS_DIR, cca, cca + '-' + requirement + '-' + model + '-temp' + str(model_temperature)+ '-fb' + str(feedback_level)+ '-' + prompt_eng +"/run"+ str(run))
    print("Initial in {}".format(result_folder_path))
    Generation.utils.util.deleteexistingcfile(result_folder_path,DELETE_EXISTING_C_FILE)
    if not os.path.exists(result_folder_path):
        os.makedirs(result_folder_path)

    llm = Generation.utils.clients.LLM_CLIENT(model=model,result_folder=result_folder_path,temperature=model_temperature)
    llm.init_message(Generation.utils.config.PROMPT_DIR, Generation.utils.config.CCAFILEPATH[cca], requirement,pe=prompt_eng)
    llm.init_system_message()
    llm.append_message(role="user",content=llm.req)
    with open(os.path.join(os.getcwd(),llm.result_folder,"message_send_at_iteration{}.json".format(iteration)),"w") as f:
            json.dump(llm.message,f,indent=4)
    llm.send_messages_no_save()
    llm.save_last_assistant_result_to_message_history()
    llm.save_message_history()
    Generation.utils.util.save_message_of_iteration(result_folder_path,llm.latest_response_content,iteration)
    ccanewname = cca+"_"+requirement[0]+''.join(random.sample('abcdefghijklmnopqrstuvwxyz',4))
    llm.refine_response()
    llm.change_cca_name(cca=cca, newname=ccanewname)
    llm.refine_c_code()
    llm.save_result_c_file(savename=ccanewname)
    Generation.utils.util.save_makefile(result_folder_path,ccanewname)
    Generation.utils.util.save_message_of_iteration(result_folder_path,llm.latest_response_content,iteration)
    return llm,ccanewname

def feedback_prompt(result_folder_path,cca,ccanewname,requirement,model,model_temperature,newusermessage,iteration,prompt_eng):
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

def initial_gen_and_test(timestr,cca,requirement,model,temperature,run,feedback_level,prompt_eng='0shot',skip_evaluation=False):
    result = None
    necc_report = copy.deepcopy(Generation.utils.config.NECC_report_template)

    necc_report["CCABase"] = cca
    necc_report["LLMModel"] = model
    necc_report["Temperature"] = temperature
    necc_report["Requirement"] = requirement
    necc_report["FeedbackLevel"] = feedback_level
    necc_report["Prompting"] = prompt_eng

      
    try:
        llm,ccanewname = initial_prompt(timestr=timestr,cca=cca,requirement=requirement,model=model,model_temperature=temperature,iteration=0,run=run,feedback_level=feedback_level,prompt_eng=prompt_eng)
        processfolder = llm.result_folder
        if skip_evaluation:
            necc_report["CCAName"] = ccanewname
            necc_report["CCAworkFolderPath"] = processfolder
            necc_report["Score"] = -1
            necc_report["IterationName"] = 0
        else:
            score, Iteration_details, Revise_message = Generation.evaluate.test_current(processfolder=processfolder,
                                                    cca=cca,
                                                    ccanewname=ccanewname,
                                                    iteration_count=0,
                                                    timestr=timestr)
            necc_report["CCAName"] = ccanewname
            necc_report["CCAworkFolderPath"] = processfolder
            necc_report["Score"] = score
            necc_report["IterationName"] = 0
            necc_report["Evaluations"] = Iteration_details
            necc_report["ReviseMessage"] = Revise_message
        # print(score, Iteration_details, Revise_message)
    except KeyboardInterrupt:
        necc_report["Exception"] = True
        print("Got KeyboardInterrupt CTRL-C, exiting")
        necc_report["UnexpectedError"] = "CTRL-C"
        return necc_report
    except Exception as e:
        necc_report["Exception"] = True
        print(repr(e))
        print("unexpected error")
        necc_report["UnexpectedError"] = repr(e)
        return necc_report
    return necc_report