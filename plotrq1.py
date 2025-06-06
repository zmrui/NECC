import os
import json
from matplotlib import pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
from matplotlib.ticker import ScalarFormatter, MultipleLocator

def calculate_cdf(input_list):
    frequency = [input_list.count(i) for i in [0, 1, 2, 2.5, 3, 3.5, 4, 4.5, 5]]
    
    cdf = []
    cumulative = 0
    for freq in frequency:
        cumulative += freq
        cdf.append(cumulative)
    
    # print(cdf)
    return cdf

def plotcdf(path,temp0list,temp05list,temp1list,cca):

    # print(temp0list)
    # print(temp05list)
    # print(temp1list)
    matplotlib.rcParams['pdf.fonttype'] = 42
    # plt.figure(figsize=(3,1.2))
    plt.clf()
    
    xtickslist = ['0%','20%','40%','50%','60%','70%','80%','90%','100%']
    x = np.arange(9)

    cdf_temp0 =  calculate_cdf(temp0list)
    cdf_temp05 =  calculate_cdf(temp05list)
    cdf_temp1 =  calculate_cdf(temp1list)

    # print(cdf_temp0)
    if len(temp0list):
        cdf_temp0 = [item / float(len(temp0list)) for item in cdf_temp0]
    else: 
        cdf_temp0 = [0,0,0,0,0,0,0,0,0]
    if len(temp05list):
        cdf_temp05 = [item / float(len(temp05list)) for item in cdf_temp05]
    else:
        cdf_temp05 = [0,0,0,0,0,0,0,0,0]
    if len(temp1list):
        cdf_temp1 = [item / float(len(temp1list)) for item in cdf_temp1]
    else:
        cdf_temp1 = [0,0,0,0,0,0,0,0,0]


    # print(cdf_temp0)
    # print(cdf_cot)
    fig, ax = plt.subplots(figsize=(4,1.2))
    p1 = ax.plot(x,cdf_temp0,label="Temperature=0",color='#ffbe7a',marker="*")
    p1 = ax.plot(x,cdf_temp05,label="Temperature=0.5",color='#82b0d2',marker="+")
    p1 = ax.plot(x,cdf_temp1,label="Temperature=1.0",color='#aa6fb0',marker="x")


    # ax.xaxis.set_tick_params(labelrotation = 30, labelsize = 6)
    plt.xticks(x, xtickslist,font={'size':9})


    plt.ylabel("Distribution",font={'size':9},labelpad=0)
    plt.yticks(font={'size':9})
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))
    # plt.grid()
    plt.legend(prop={'size':8}, loc='lower right')
    # plt.legend(prop={'size':6},loc=2, bbox_to_anchor=(1.0, 1.0),ncol=1)
    plt.xlabel("satisfaction percentage",font={'size':9},labelpad=0)
    plt.ylim((-0.1,1.1))
    plt.tick_params(axis='x', pad=2)
    plt.tick_params(axis='y', pad=2)
    # plt.show()

    plt.title(f"CDF for {cca.title()} code base results",font={'size':8}, loc='left')
    plt.savefig(f'{path}/rq1_re2{cca}.png', dpi=300, bbox_inches='tight', pad_inches=0.01)
    plt.savefig(f'{path}/rq1_re2{cca}.pdf', dpi=300, bbox_inches='tight', pad_inches=0.01)



res_base_path = "/mnt/ICC2025_res/RQ1/"

dirs = os.listdir(res_base_path)

exp2_dirs = [item for item in dirs if os.path.isdir(os.path.join(res_base_path, item))]

print(exp2_dirs)

# exp2_dirs = [item for item in dirs if "exp1" in item]


# reno_0shot_results_score = []
# reno_cot_results_score = []
# cubic_0shot_results_score = []
# cubic_cot_results_score = []
# vegas_0shot_results_score = []
# vegas_cot_results_score = []
# illinois_0shot_results_score = []
# illinois_cot_results_score = []

cnt = 0

for cca in ['reno','cubic','illinois','vegas']:
    cca_temp0_cot_result_score = []
    cca_temp0_0shot_result_score = []
    cca_temp05_cot_result_score = []
    cca_temp05_0shot_result_score = []
    cca_temp1_cot_result_score = []
    cca_temp1_0shot_result_score = []
    for temp in ['temp0_','temp0.5_','temp1']:
        for pe in ['0shot','cot']:

            print(f"current:{cca} {temp} {pe}")
            for exp2_res_dir in exp2_dirs:
                subdir = os.path.join(res_base_path,exp2_res_dir)
                sub_res = os.listdir(subdir)

                
                for item2 in sub_res:
                    param_dirs_path =  os.path.join(subdir,item2)
                    "/mnt/ICC2025_res/RQ1/reno/reno-throughtput-gpt-4o-2024-08-06-temp1-fb5-0shot"

                    param_dirs = os.listdir(param_dirs_path)
                    # print(run_dirs)
                    jsonfile = [item for item in param_dirs if item.endswith(".json")]

                    for item in jsonfile:
                        
                        # print(item)
                        score = 0
                        fullpath = os.path.join(param_dirs_path,item)
                        
                        # print(run_dir)
                        if "exception" in item:
                            score = 0
                        elif item.startswith("Evaliation_History") and item.endswith(".json"):
                            with open(fullpath, 'r') as file:
                                jsondata = json.load(file)
                                score = jsondata[0]["Scores"][0]
                        # print(score)
                        if  cca in item and "cot" in item and 'temp0.0' in item:
                            cca_temp0_cot_result_score.append(score)
                        elif cca in item and "0shot" in item and 'temp0.0' in item:
                            cca_temp0_0shot_result_score.append(score)
                        elif cca in item and "cot" in item and 'temp0.5' in item:
                            cca_temp05_cot_result_score.append(score)
                        elif cca in item and "0shot" in item and 'temp0.5' in item:
                            cca_temp05_0shot_result_score.append(score)
                        elif cca in item and "cot" in item and 'temp1.0' in item:
                            cca_temp1_cot_result_score.append(score)
                        elif cca in item and "0shot" in item and 'temp1.0' in item:
                            cca_temp1_0shot_result_score.append(score)

    # print(cca_temp0_cot_result_score)
    # print(cca_temp0_0shot_result_score)
    # print(cca_temp05_cot_result_score)
    # print(cca_temp05_0shot_result_score)
    # print(cca_temp1_cot_result_score)
    # print(cca_temp1_0shot_result_score)

    plotcdf(path="Plots",
            temp0list=cca_temp0_0shot_result_score,
            temp05list=cca_temp05_0shot_result_score,
            temp1list=cca_temp1_0shot_result_score,
            cca=f"{cca} 0-shot")
    plotcdf(path="Plots",
            temp0list=cca_temp0_cot_result_score,
            temp05list=cca_temp05_cot_result_score,
            temp1list=cca_temp1_cot_result_score,
            cca=f"{cca} CoT")