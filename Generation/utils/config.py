import os

ENABLE_LIMIT = True

USER = ""

ROOTDIR = ""

TEMPLATE_DIR = os.path.join(ROOTDIR,"TCP_CCAs_in_BPF")

PROMPT_DIR = os.path.join(ROOTDIR,"Prompts")

RESULTS_DIR = os.path.join(ROOTDIR,"Results")
RUNLOG_DIR = os.path.join(ROOTDIR,"Runlog")

REEVAL_DIR = os.path.join(ROOTDIR,"Re_evaluate")

HEADER_DIR = os.path.join(TEMPLATE_DIR,"headers")

CUBIC_DIR = os.path.join(TEMPLATE_DIR,"bpf_cubic")
BPF_CUBIC_FILE = os.path.join(CUBIC_DIR,"bpf_cubic.c")


ILLINOIS_DIR = os.path.join(TEMPLATE_DIR,"bpf_illinois")
BPF_ILLINOIS_FILE = os.path.join(ILLINOIS_DIR,"bpf_illinois.c")


RENO_DIR = os.path.join(TEMPLATE_DIR,"bpf_reno")
BPF_RENO_FILE = os.path.join(RENO_DIR,"bpf_reno.c")


VEGAS_DIR = os.path.join(TEMPLATE_DIR,"bpf_vegas")
BPF_VEGAS_FILE = os.path.join(VEGAS_DIR,"bpf_vegas.c")

BBR_DIR = os.path.join(TEMPLATE_DIR,"bpf_bbr")
BPF_BBR_FILE = os.path.join(BBR_DIR,"bpf_bbr.c")

MININET_RESULT_DIR = os.path.join(ROOTDIR,"Mininet_testbed","results","Dumbell")

CCAFILEPATH = {
    "cubic":BPF_CUBIC_FILE,
    "illinois":BPF_ILLINOIS_FILE,
    "reno":BPF_RENO_FILE,
    "vegas":BPF_VEGAS_FILE,
    'bbr':BPF_BBR_FILE
}

MAX_ITERATION = 5
ITERATION_COUNT = 0
NEED_REMOVE_PREVIOUS = False

HOME_INTERNET_BW = 60
HOME_BW_LIMIT=31
REQ_BW = 12

begin_flag = "#define BEGIN_SOURCE_CODE 3"
end_flag = "#define END_SOURCE_CODE 3"

makefile_text = '''
Clang=clang -O2 -target bpf -c -g
default:	{}
clean:
	-rm *.o
{}:
	$(Clang) {}.c -o {}.o -I {}
register:
	bpftool struct_ops register {}.o
'''

revise_prompt_text = '''
The generated result has following errors, please revise it and output full source code.
{}
'''

revise_prompt_text_None = '''
The previous generated result does not achieve the design goals, please try again.
'''

NECC_report_template = {
    "CCAName":None,
    "Exception":False,
    "UnexpectedError":None,
    "CCAworkFolderPath":None,
    "CCABase":None,
    "LLMModel":None,
    "Prompting":None,
    "Temperature":None,
    "Requirement":None,
    "FeedbackLevel":None,
    'Score':None,
    "IterationName":None,
    "Evaluations":[],
    "ReviseMessage": [] #ReviseMessage containes only failed evaluation information. Other strategies could use ["Message"] informatin from Evaluation_item
}

Evaluation_item_template = {
    "EvaluationItemName":None,
    "Result":None,
    "FailReason":None,
    "Message":None
}
