import utils.config
import utils.util
import subprocess
import os
import json


def get_name(path):
    files_list = os.listdir(path)
    for file in files_list:
        if file.endswith('.o'):
            ccaname = file.replace('.o','')
            return ccaname


if __name__ == '__main__':
    
    reno_varients = []
    cubic_varients = []
    illinois_varients = []
    vegas_varients = []

    if utils.util.prompt_sudo() != 0:
         print("needs root permision")
         exit()

    all_cca_varients_result_list = []
    with open('all_cca_varients_result_list.txt','r') as f:
        all_cca_varients_result_list = f.readlines()

    # with open('generated_cca_varients.json','r') as f:
    #     cca_varients = json.load(f)

    utils.util.remove_all_bpf_ccas()
    print("++++++++++++++++++++++++++++++++++++")
    for ccapath in all_cca_varients_result_list:
        target_path = ccapath.replace('\n','')
        ccaname = get_name(target_path)
        make_reg_command = ["make","register"]
        reg_proc = subprocess.Popen(make_reg_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=target_path)
        stdout, stderr = reg_proc.communicate()
        print("bpftool struct_ops Reg Output:")
        print(stdout)
        if utils.util.check_cca_exist(ccaname):
            if 'cubic'in ccaname :
                cubic_varients.append(ccaname)
            elif 'reno' in ccaname :
                reno_varients.append(ccaname)
            elif 'illinois' in ccaname :
                illinois_varients.append(ccaname)
            elif 'vegas' in ccaname :
                vegas_varients.append(ccaname)
        print("++++++++++++++++++++++++++++++++++++")
    cca_varients = {'reno':reno_varients,
                'cubic':cubic_varients,
                'illinois':illinois_varients,
                'vegas':vegas_varients}
    with open('available_cca_varients.json','w') as f:
        json.dump(cca_varients,f)
    print(cca_varients)