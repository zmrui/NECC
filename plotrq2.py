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

def plotcdf(path,cotlist,shot0list,cca):
    matplotlib.rcParams['pdf.fonttype'] = 42
    # plt.figure(figsize=(3,1.2))
    plt.clf()
    
    xtickslist = ['0%','20%','40%','50%','60%','70%','80%','90%','100%']
    x = np.arange(9)

    cdf_0shot =  calculate_cdf(shot0list)
    cdf_cot = calculate_cdf(cotlist)

    cdf_0shot = [item / float(len(shot0list)) for item in cdf_0shot]
    cdf_cot = [item / float(len(cotlist)) for item in cdf_cot]

    # print(cdf_0shot)
    # print(cdf_cot)
    fig, ax = plt.subplots(figsize=(4,1.2))
    p1 = ax.plot(x,cdf_0shot,label="0-shot",color='#ffbe7a',marker="*")
    p1 = ax.plot(x,cdf_cot,label="CoT",color='#82b0d2',marker="+")


    # ax.xaxis.set_tick_params(labelrotation = 30, labelsize = 6)
    plt.xticks(x, xtickslist,font={'size':9})


    plt.ylabel("Distribution",font={'size':9},labelpad=0)
    plt.yticks(font={'size':9})
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))
    # plt.grid()
    plt.legend()
    # plt.legend(prop={'size':6},loc=2, bbox_to_anchor=(1.0, 1.0),ncol=1)
    plt.xlabel("satisfaction percentage",font={'size':9},labelpad=0)
    plt.tick_params(axis='x', pad=2)
    plt.tick_params(axis='y', pad=2)
    # plt.show()

    plt.title(f"CDF for {cca} code base results",font={'size':8}, loc='left')
    plt.savefig(f'{path}/r2{cca}.png', dpi=300, bbox_inches='tight', pad_inches=0.01)
    plt.savefig(f'{path}/r2{cca}.pdf', dpi=300, bbox_inches='tight', pad_inches=0.01)



res_base_path = "/mnt/ICC2025_res/RQ1/"

dirs = os.listdir(res_base_path)

exp2_dirs = [item for item in dirs if os.path.isdir(os.path.join(res_base_path, item))]

# print(exp2_dirs)

reno_0shot_results_score = []
reno_cot_results_score = []
cubic_0shot_results_score = []
cubic_cot_results_score = []
vegas_0shot_results_score = []
vegas_cot_results_score = []
illinois_0shot_results_score = []
illinois_cot_results_score = []

cnt = 0
for cca in ['reno','cubic','illinois','vegas']:
    for temp in ['temp0.5_']:
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
        
                        if "reno" in item and "0shot" in item and 'temp0.5' in item:
                            reno_0shot_results_score.append(score)
                        elif "reno" in item and "cot" in item and 'temp0.5' in item:
                            reno_cot_results_score.append(score)

                        elif "cubic" in item and "cot" in item and 'temp0.5' in item:
                            cubic_cot_results_score.append(score)
                        elif "cubic" in item and "0shot" in item and 'temp0.5' in item:
                            cubic_0shot_results_score.append(score)

                        elif "vegas" in item and "cot" in item and 'temp0.5' in item:
                            vegas_cot_results_score.append(score)
                        elif "vegas" in item and "0shot" in item and 'temp0.5' in item:
                            vegas_0shot_results_score.append(score)

                        elif "illinois" in item and "cot" in item and 'temp0.5' in item:
                            illinois_cot_results_score.append(score)
                        elif "illinois" in item and "0shot" in item and 'temp0.5' in item:
                            illinois_0shot_results_score.append(score)

# print(reno_0shot_results_score) 
# print(reno_cot_results_score )
# print(cubic_0shot_results_score )
# print(cubic_cot_results_score )
# print(vegas_0shot_results_score )
# print(vegas_cot_results_score )
# print(illinois_0shot_results_score )
# print(illinois_cot_results_score )

plotcdf(path="Plots",cotlist=reno_cot_results_score[:30],shot0list=reno_0shot_results_score[:30],cca="Reno")
plotcdf(path="Plots",cotlist=cubic_cot_results_score[:30],shot0list=cubic_0shot_results_score[:30],cca="Cubic")
plotcdf(path="Plots",cotlist=vegas_cot_results_score[:30],shot0list=vegas_0shot_results_score[:30],cca="Vegas")
plotcdf(path="Plots",cotlist=illinois_cot_results_score[:30],shot0list=illinois_0shot_results_score[:30],cca="Illinois")