
import os
import Generation.utils.config
import shutil
import subprocess

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
    
def load_message_from_folder(folder,role):
    if role == "fullref":
        ref = open(os.path.join(folder,"fullref"),"r").read()
        req = open(os.path.join(folder,"requirement"),"r").read()
        sysmeg = open(os.path.join(folder,"sytemprompt"),"r").read()
    else:
        pass

    return ref,req,sysmeg
def get_prompts(prompt_folder,prompt):
    files = os.listdir(prompt_folder)
    if prompt in files:
        return True
    else:
        return False
def load_message_direct(prompt_folder, cca_path, pe, requirement='throughtput'):
    reference = open(os.path.join(prompt_folder,"gen_variable"),"r").read()
    ccacode = open(cca_path,"r").read()
    req = open(os.path.join(prompt_folder,requirement),"r").read()
    if pe == 'cot':
        sysmeg = open(os.path.join(prompt_folder,"cot_system_prompt"),"r").read()
    elif pe == '0shot':
        sysmeg = open(os.path.join(prompt_folder,"system_prompt"),"r").read()
    elif get_prompts(prompt_folder,pe):
        sysmeg = open(os.path.join(prompt_folder,pe),"r").read()
    else:
        sysmeg = open(os.path.join(prompt_folder,"system_prompt"),"r").read()
    
    limitation = open(os.path.join(prompt_folder,"limitation"),"r").read()

    code = '<reference>'+reference+'</reference>\n<code>\n'+ccacode+'\n</code>'
    if Generation.utils.config.ENABLE_LIMIT:
        req = req + limitation

    return code, req, sysmeg

def save_makefile(path,ccaname):
    with open (os.path.join(path,"Makefile"),'w') as f:
        f.write(Generation.utils.config.makefile_text.format(ccaname,ccaname,ccaname,ccaname,Generation.utils.config.HEADER_DIR,ccaname))
def save_message_of_iteration(path,content,iteration):
    with open (os.path.join(path,"response_iteration{}.md".format(iteration)),'w') as f:
        f.write(content)
def mnclean():
    check_command = ["mn","-c"]
    make_proc = subprocess.Popen(check_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
def deleteexistingcfile(folder,enabled):
    if enabled:
        if os.path.exists(folder):
            files = os.listdir(folder)
            for file in files:
                if file.endswith(".c") or file.endswith(".o"):
                    os.remove(os.path.join(folder,file))

def check_cca_exist(ccaname):
    check_command = ["sysctl","net.ipv4.tcp_available_congestion_control"]
    make_proc = subprocess.Popen(check_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = make_proc.communicate()
    stdoutstr = stdout.decode()
    print(stdoutstr)
    if ccaname in stdoutstr:
        print(ccaname,'success')
        return True
    else:
        print(ccaname,'not found')
        return False
def remove_all_bpf_ccas():
    systemcca('cubic')
    check_command = ["bpftool","struct_ops","list"]
    check_proc = subprocess.Popen(check_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = check_proc.communicate()
    stdoutstr = stdout.decode()
    lines = stdoutstr.split('\n')
    # print(lines)
    flag = True
    for line in lines:
        if ':' in line:
            bpf_id = str(line.split(":")[0])
            unreg_command = ["sudo","bpftool","struct_ops","unregister", "id", bpf_id]
            unreg_proc = subprocess.Popen(unreg_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr = unreg_proc.communicate()
            stdoutstr = stdout.decode()
            if 'Unregistered' in stdoutstr:
                print(stdoutstr)
            else:
                print('Unregister failed, id:', bpf_id)
                flag = False
    check_command = ["sysctl","net.ipv4.tcp_available_congestion_control"]
    make_proc = subprocess.Popen(check_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = make_proc.communicate()
    stdoutstr = stdout.decode()
    print(stdoutstr)
    return flag

def prompt_sudo():
    ret = 0
    if os.geteuid() != 0:
        msg = "[sudo] password for %u:"
        ret = subprocess.check_call("sudo -v -p '%s'" % msg, shell=True)
    return ret