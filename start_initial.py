import Generation.utils.util 
import Generation.utils.clients 
import Generation.utils.config 
import Generation.utils.variable 
import Generation.generate_new
import os
import json
import shutil
from datetime import datetime

FEEDBACKLIST = [5]

# ============================================================
# Running parameter setting
REQUIREMENTLIST = ['throughtput']
PELIST = ['cot']
CCALIST = ['reno','cubic']
TEMPERATURELIST = [0.5]
# MODELS =  ['gpt-4o-2024-08-06']
MODELS = ["gpt-4o-mini"]
RUN = 5
# ==============Debugging Flags==============
DRY_RUN = False
# If set True, then will only enumerate and print the the parameters that will be executed. 

SKIP_EVALUATION=True
# If set True, then will only sent request and save results, and skip evaluation.
# ============================================================
Generation.utils.config.HOME_INTERNET_BW = 60
Generation.utils.config.HOME_BW_LIMIT = 31
Generation.utils.config.REQ_BW = 12

Generation.generate_new.DELETE_EXISTING_C_FILE = True
Generation.utils.config.ENABLE_LIMIT = True


RUNLOG = "Runlog"

def clear_previous_results():
    shutil.rmtree(Generation.utils.config.MININET_RESULT_DIR)

def main():
    now = datetime.now()
    dt_string = "RQ1_"+now.strftime("%Y-%m-%d-%Hh.%Mm.%Ss")
    Generation.utils.config.RESULTS_DIR = os.path.join(Generation.utils.config.RESULTS_DIR, dt_string)
    os.makedirs(Generation.utils.config.RESULTS_DIR)
    Generation.utils.config.RUNLOG_DIR = os.path.join(Generation.utils.config.RUNLOG_DIR, dt_string)
    os.makedirs(Generation.utils.config.RUNLOG_DIR)
    # clear_previous_results()
    Generation.utils.util.remove_all_bpf_ccas()

    for cca in CCALIST:
        for requirement in RERUIREMENTLIST:
            for model in MODELS:
                for temperature in TEMPERATURELIST:
                    for fb in FEEDBACKLIST:
                        for prompt in PELIST:
                            for run in range(RUN):
                                print(datetime.now())
                                Generation.utils.util.remove_all_bpf_ccas()
                                Iteration_history = []
                                print("=================================================================")
                                print(f"cca={cca} req={requirement} model={model} temperature={temperature} feedbacklevel={fb} run={run}")
                                if DRY_RUN:
                                    continue
                                necc_report_item=Generation.generate_new.initial_gen_and_test(skip_evaluation=SKIP_EVALUATION,timestr=dt_string,cca=cca,requirement=requirement,model=model,temperature=temperature,feedback_level=fb,run=run,prompt_eng=prompt)
                                Score = necc_report_item["Score"]
                                ccaname = necc_report_item["CCAName"]
                                CCAworkFolderPath = necc_report_item["CCAworkFolderPath"]
                                hasexception = necc_report_item['Exception']
                                Iteration_history.append(necc_report_item)
                                if hasexception:
                                    with open(f'{CCAworkFolderPath}/report.json','w') as f:
                                        json.dump(Iteration_history,f,indent=4)
                                    if necc_report_item['UnexpectedError'] == "CTRL-C":
                                        os.system(F"sudo chown -R {Generation.utils.config.USER} {Generation.utils.config.ROOTDIR}")
                                        exit()
                                else:
                                    with open(f'{CCAworkFolderPath}/report.json','w') as f:
                                        json.dump(Iteration_history,f,indent=4)

                                os.system('sudo mn -c')
    if DRY_RUN:
        return

    os.system(F"sudo chown -R {Generation.utils.config.USER} {Generation.utils.config.ROOTDIR}")

    # return success

if __name__ == '__main__':
    if len(Generation.utils.config.USER) == 0 or len(Generation.utils.config.ROOTDIR) == 0:
        print("Config 'USER' and 'ROOTDIR' in Generation/utils/config.py")
        exit()
    main()
