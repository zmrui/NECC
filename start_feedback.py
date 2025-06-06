import os
import shutil
import json
from matplotlib import pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
import copy
from matplotlib.ticker import ScalarFormatter, MultipleLocator
import Generation.evaluate
import Generation.utils.util
import Generation.utils.config
from datetime import datetime
import Generation.feedbackv2

def ProcessMessage(Revise_message:list):
    if Revise_message is None:
        return ""
    result = ""
    for i in range(len(Revise_message)):
        messageitem = Revise_message[i]
        result = result + f"[{i}]. {messageitem} \n"
    return result
# ============================================================
# Running parameter setting

#This controls which cca will be feedback. For example, if set reno, then skipped non-reno folder
CCALIST = ['reno']

REPORT_LOG_BASE = f"/home/ubuntu/NECC/Results"

#Source folder
Feedback_from = "RQ1_2025-03-10-11h.40m.53s"
SCRSTORPATH = os.path.join(REPORT_LOG_BASE,Feedback_from)

#Destination folder
Feedback_to = "RQ4/Feedback1"
DSTSHORPATH = os.path.join(REPORT_LOG_BASE,Feedback_to)

# FEEDBACK_ITERATION = 0 ---> Initial prompt results
# FEEDBACK_ITERATION = 1 ---> First feedback on Initial prompt results
# FEEDBACK_ITERATION = 2 ---> Second feedback on First feedback results
FEEDBACK_ITERATION = 1

# ============================================================
# =============Debugging Flags=============
# If set Ture, then will skip evaluation and feedback prompt, only do copy files
DRY_RUN = False                          

# If set Ture, then evaluation and feedback prompt will return 0 or [], and do not run real evaluation and do not send request via API
SKIP = True                              
# =========================================

RUNLOG = "Runlog"

def main():

    "/mnt/nrdstor/ICC2025_res/RQ1/"

    for cca in CCALIST:
        CCA_paths = os.path.join(SCRSTORPATH,cca)
        "/mnt/nrdstor/ICC2025_res/RQ1/cubic"

        CCA_Params_paths = os.listdir(CCA_paths)

        # print(CCA_Params_paths)
        for cca_param_path in CCA_Params_paths:


            cca_param_path_abs = os.path.join(CCA_paths,cca_param_path)
            "/mnt/nrdstor/ICC2025_res/RQ1/cubic/cubic-throughtput-gpt-4o-2024-08-06-temp0.5-fb5-0shot"

            RUNDIR = os.listdir(cca_param_path_abs)
            # print(RUNDIR)
            RUNDIRS = [item for item in RUNDIR if os.path.isdir(os.path.join(cca_param_path_abs, item))]
            for run in RUNDIRS:
                original_run_path = os.path.join(cca_param_path_abs,run)
                "/mnt/nrdstor/ICC2025_res/RQ1/cubic/cubic-throughtput-gpt-4o-2024-08-06-temp0.5-fb5-cot/run13"
                

                dst_feedback_run_path = original_run_path.replace(Feedback_from, Feedback_to)
                "/mnt/nrdstor/ICC2025_res/RQ4/Feedback1/cubic/cubic-throughtput-gpt-4o-2024-08-06-temp0.5-fb5-cot/run17"

                if os.path.exists(dst_feedback_run_path):
                    print(f"[Skip] From{original_run_path} \n To {dst_feedback_run_path}")
                    continue
                else:
                    # os.makedirs(dst_feedback_run_path)
                    print(f"From {original_run_path} \n To {dst_feedback_run_path}")
                    shutil.copytree(original_run_path, dst_feedback_run_path)

                original_json_file_path =  os.path.join(original_run_path,"report.json")

        
                # begin iteration
                Generation.utils.config.RESULTS_DIR = dst_feedback_run_path.replace(REPORT_LOG_BASE,RUNLOG)
                
                previous_log, full_log = Generation.feedbackv2.load_from_json_result(original_json_file_path,FEEDBACK_ITERATION-1)

                CCAName = previous_log["CCAName"]
                ccanewname = CCAName
                Exception = previous_log["Exception"]
                Prompting = previous_log["Prompting"]
                UnexpectedError = previous_log["UnexpectedError"]
                CCAworkFolderPath = previous_log["CCAworkFolderPath"]
                CCABase = previous_log["CCABase"]
                LLMModel = previous_log["LLMModel"]
                Temperature = previous_log["Temperature"]
                Requirement = previous_log["Requirement"]
                FeedbackLevel = previous_log["FeedbackLevel"]
                Score = previous_log["Score"]
                IterationName = previous_log["IterationName"]
                # Evaluations = previous_log["Evaluations"]
                ReviseMessage = previous_log["ReviseMessage"]

                new_working_path = dst_feedback_run_path

                # Generation.feedbackv2.copyanything(src=original_run_path,dst=new_working_path)

                Iteration_history = [full_log]
                if not DRY_RUN:
                    necc_report = copy.deepcopy(Generation.utils.config.NECC_report_template)

                    # necc_report["CCABase"] = CCABase
                    # necc_report["LLMModel"] = LLMModel
                    # necc_report["Temperature"] = Temperature
                    # necc_report["Requirement"] = Requirement
                    # necc_report["FeedbackLevel"] = FeedbackLevel
                    # necc_report["Prompting"] = Prompting

                    # score, Iteration_details, Revise_message = Generation.feedbackv2.test_current(processfolder=new_working_path,cca=CCABase,ccanewname=ccanewname,iteration_count=1,timestr=run)
                    # scores.append(score)
                    # print(scores)
                    # Iterations.append(Iteration_details)

                    Previous_Revise_message = ProcessMessage(ReviseMessage)
                    print(f"Previous_Revise_message\n{Previous_Revise_message}")
                    if Score < 5:
                        necc_report = copy.deepcopy(previous_log)
                        Generation.feedbackv2.feedback_prompt(skip=SKIP,
                                    result_folder_path=new_working_path,
                                    cca=CCABase,ccanewname=ccanewname,
                                    requirement=Requirement,model=LLMModel,
                                    model_temperature=Temperature,
                                    newusermessage=Previous_Revise_message,
                                    iteration=FEEDBACK_ITERATION,prompt_eng=Prompting)

                        score, Iteration_details, Revise_message = Generation.evaluate.test_current(skip=SKIP,
                                                    processfolder=new_working_path,
                                                    cca=cca,
                                                    ccanewname=ccanewname,
                                                    iteration_count=0,
                                                    timestr="")
                        
                        # necc_report["CCAName"] = ccanewname
                        necc_report["CCAworkFolderPath"] = new_working_path
                        necc_report["Score"] = score
                        necc_report["IterationName"] = FEEDBACK_ITERATION
                        necc_report["Evaluations"] = Iteration_details
                        necc_report["ReviseMessage"] = Revise_message

                        Iteration_history.append(necc_report)


                    with open(os.path.join(dst_feedback_run_path,f'report.json'),'w') as f:
                                                json.dump(Iteration_history,f,indent=4)
                    
                    Generation.utils.util.remove_all_bpf_ccas()

    os.system(F"sudo chown -R {Generation.utils.config.USER} {Generation.utils.config.ROOTDIR}")
    

if __name__ == "__main__":
    if len(Generation.utils.config.USER) == 0 or len(Generation.utils.config.ROOTDIR) == 0:
        print("Config 'USER' and 'ROOTDIR' in Generation/utils/config.py")
        exit()
    main()