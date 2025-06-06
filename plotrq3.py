import os
from matplotlib import pyplot as plt
import matplotlib
import json
import pandas as pd
import numpy as np
from matplotlib.ticker import ScalarFormatter, MultipleLocator,PercentFormatter
def calculate_cdf(input_list):
    frequency = [input_list.count(i) for i in [0, 1, 2, 2.5, 3, 3.5, 4, 4.5, 5]]
    
    cdf = []
    cumulative = 0
    for freq in frequency:
        cumulative += freq
        cdf.append(cumulative)
    
    # print(cdf)
    return cdf


if __name__ == '__main__':

    res_base_path = "/mnt/ICC2025_res/RQ1/"

    dirs = os.listdir(res_base_path)

    exp2_dirs = [item for item in dirs if os.path.isdir(os.path.join(res_base_path, item))]

    # print(exp2_dirs)

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

    for cca in ['cubic']:
        cca_temp0_cot_result_score = []
        cca_temp0_0shot_result_score = []
        cca_temp05_cot_result_score = []
        cca_temp05_0shot_result_score = []
        cca_temp1_cot_result_score = []
        cca_temp1_0shot_result_score = []
        for temp in ['temp0.5_']:
            for pe in ['cot']:

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
    matplotlib.rcParams['pdf.fonttype'] = 42
    # plt.figure(figsize=(6,2))
    plt.clf()
    print(cca_temp05_cot_result_score)
    poolsize = range(1,31)
    Maxscore = np.array(sorted(cca_temp05_cot_result_score))
    Maxscore = Maxscore/5.0
    price = 0.07257 * np.arange(1,31)
    # print(price)
    fig = plt.figure()
    # ax = fig.add_subplot()
    fig, ax = plt.subplots(figsize=(6,1.3))
    ax.plot(poolsize, Maxscore, color='darkorange', marker='x', markersize = 6, linewidth=2, label = 'Highest Score')
    ax2 = ax.twinx()
    ax2.plot(poolsize, price, color='steelblue', marker='+',markersize = 6, linewidth=2, label = 'Cost')
    ax.legend(loc=2)
    # ax.set_ylim(0,5)
    # ax.yaxis.set_major_locator(MultipleLocator(1))
    # ax.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax.set_ylabel("Highest Score")
    ax.set_xlabel("Pool Size",labelpad=0)
    # ax.grid()
    # ax2.set_ylim(0, 35)
    ax2.set_ylim(0,2.3)
    ax.set_ylim(0,1.1)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    # ax.yaxis.set_minor_formatter(PercentFormatter(1))
    # ax.yaxis.set_minor_formatter(PercentFormatter(0.1,1))
    ax2.xaxis.set_major_locator(MultipleLocator(2))
    ax2.set_ylabel("Cost $USD")
    ax2.yaxis.set_major_locator(MultipleLocator(0.5))
    # ax2.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax2.legend(loc=4)
    

    ax2.set_xlabel("")
    # plt.xlabel("Pool size",font={'size':8},labelpad=0)
    # plt.ylim(0,6)
    plt.tick_params(axis='x', pad=2)
    plt.tick_params(axis='y', pad=2)
    # plt.show()

    # plt.title("Poolsize impact to CDF",font={'size':8}, loc='left')
    plt.title("Pool size Impact on Highest Satisfaction Score and Cost",font={'size':10}, loc='left')
    plt.savefig('poolsize.png', dpi=720, bbox_inches='tight', pad_inches=0.01)
    plt.savefig('poolsize.pdf', dpi=720, bbox_inches='tight', pad_inches=0.01)
