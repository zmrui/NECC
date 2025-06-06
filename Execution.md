## To run initial prompts:

bpf and mininet needs sudo/root privilege

### Running parameter setting
```py

# Running parameter setting
REQUIREMENTLIST = ['throughtput'] 	# Requirement. To add more, add "xxxx" file to 'NECC/Prompts' folder and give same "xxxx" as parameter here.
PELIST = ['cot']			# Prompt engineering strategies. To add more, add "xxxx" file to 'NECC/Prompts' folder and give same "xxxx" as parameter here.
CCALIST = ['cubic']			# Base CCA source code
TEMPERATURELIST = [0.5]			# Model temperature
MODELS =  ['gpt-4o-mini-2024-07-18']	

# For each combination, run RUN times.
RUN = 5
```

### Debug Flags

```py
# ==============Debugging Flags==============
# If set True, then will only enumerate and print the the parameters that will be executed. 
DRY_RUN = False

# If set True, then will only sent request and save results, and skip evaluation.
SKIP_EVALUATION=True
```

### Execution command
```
sudo python3 start_initial.py
```

### Result structure
It will generate results in Results folder

Example structure:
```
/home/ubuntu/NECC/Results
├── RQ1_2025-03-10-10h.02m.32s
│   └── reno
│       └── reno-throughtput-gpt-4o-mini-temp0.5-fb5-cot
│           ├── run0
│           │   ├── Makefile
│           │   ├── latest_message
│           │   ├── message_send_at_iteration0.json
│           │   ├── reno_tnjsr.c
│           │   ├── report.json
│           │   └── response_iteration0.md
│           ├── run1
│           │   ├── Makefile
│           │   ├── latest_message
│           │   ├── message_send_at_iteration0.json
│           │   ├── reno_tphjv.c
│           │   ├── report.json
│           │   └── response_iteration0.md
│           ├── run2
│           │   ├── Makefile
│           │   ├── latest_message
│           │   ├── message_send_at_iteration0.json
│           │   ├── reno_trckv.c
│           │   ├── report.json
│           │   └── response_iteration0.md
└── RQ1_2025-03-10-11h.40m.53s
    ├── cubic
    │   └── cubic-throughtput-gpt-4o-mini-temp0.5-fb5-cot
    │       ├── run0
    │       │   ├── Makefile
    │       │   ├── cubic_tmxwd.c
    │       │   ├── latest_message
    │       │   ├── message_send_at_iteration0.json
    │       │   ├── report.json
    │       │   └── response_iteration0.md
    │       ├── run1
    │       │   ├── Makefile
    │       │   ├── cubic_tcmbw.c
    │       │   ├── latest_message
    │       │   ├── message_send_at_iteration0.json
    │       │   ├── report.json
    │       │   └── response_iteration0.md
    │       ├── run2
    │           ├── Makefile
    │           ├── cubic_tkblr.c
    │           ├── latest_message
    │           ├── message_send_at_iteration0.json
    │           ├── report.json
    │           └── response_iteration0.md
    └── reno
        └── reno-throughtput-gpt-4o-mini-temp0.5-fb5-cot
            ├── run0
            │   ├── Makefile
            │   ├── latest_message
            │   ├── message_send_at_iteration0.json
            │   ├── reno_tcdrt.c
            │   ├── report.json
            │   └── response_iteration0.md
            ├── run1
            │   ├── Makefile
            │   ├── latest_message
            │   ├── message_send_at_iteration0.json
            │   ├── reno_twfvz.c
            │   ├── report.json
            │   └── response_iteration0.md
            ├── run2
            │   ├── Makefile
            │   ├── latest_message
            │   ├── message_send_at_iteration0.json
            │   ├── reno_tqcpz.c
            │   ├── report.json
            │   └── response_iteration0.md
```


## To run feedback prompts:

### Running parameter setting
Config those parameters in ```start_feedback.py``` file
```python
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
FEEDBACK_ITERATION = 1 # ---> Please manually increase this number at each iteration
```

### Debug Flags
```py
# If set Ture, then will skip evaluation and feedback prompt, only do copy files
DRY_RUN = False                          

# If set Ture, then evaluation and feedback prompt will return 0 or [], and do not run real evaluation and do not send request via API
SKIP = True        
```

### Execution command

```
sudo python3 start_feedback.py
```

### Example

The example config above will copy from ```/home/ubuntu/NECC/Results/RQ1_2025-03-10-11h.40m.53s```

To ```/home/ubuntu/NECC/Results/RQ4/Feedback1```

Then feedback, revise, evaluate and save results to ```/home/ubuntu/NECC/Results/RQ4/Feedback1```


### Result structure
```
/home/ubuntu/NECC/Results
├── RQ1_2025-03-10-11h.40m.53s
│   ├── cubic
│   │   └── cubic-throughtput-gpt-4o-mini-temp0.5-fb5-cot
│   │       ├── run0
│   │       │   ├── Makefile
│   │       │   ├── cubic_tmxwd.c
│   │       │   ├── latest_message
│   │       │   ├── message_send_at_iteration0.json
│   │       │   ├── report.json
│   │       │   └── response_iteration0.md
│   │       ├── run1
│   │       │   ├── Makefile
│   │       │   ├── cubic_tcmbw.c
│   │       │   ├── latest_message
│   │       │   ├── message_send_at_iteration0.json
│   │       │   ├── report.json
│   │       │   └── response_iteration0.md
│   │       ├── run2
│   │       │   ├── Makefile
│   │       │   ├── cubic_tkblr.c
│   │       │   ├── latest_message
│   │       │   ├── message_send_at_iteration0.json
│   │       │   ├── report.json
│   │       │   └── response_iteration0.md
│   │       ├── run3
│   │       │   ├── Makefile
│   │       │   ├── cubic_tqczg.c
│   │       │   ├── latest_message
│   │       │   ├── message_send_at_iteration0.json
│   │       │   ├── report.json
│   │       │   └── response_iteration0.md
│   │       └── run4
│   │           └── message_send_at_iteration0.json
│   └── reno
│       └── reno-throughtput-gpt-4o-mini-temp0.5-fb5-cot
│           ├── run0
│           │   ├── Makefile
│           │   ├── latest_message
│           │   ├── message_send_at_iteration0.json
│           │   ├── reno_tcdrt.c
│           │   ├── report.json
│           │   └── response_iteration0.md
│           ├── run1
│           │   ├── Makefile
│           │   ├── latest_message
│           │   ├── message_send_at_iteration0.json
│           │   ├── reno_twfvz.c
│           │   ├── report.json
│           │   └── response_iteration0.md
│           ├── run2
│           │   ├── Makefile
│           │   ├── latest_message
│           │   ├── message_send_at_iteration0.json
│           │   ├── reno_tqcpz.c
│           │   ├── report.json
│           │   └── response_iteration0.md
│           ├── run3
│           │   ├── Makefile
│           │   ├── latest_message
│           │   ├── message_send_at_iteration0.json
│           │   ├── reno_tqhrx.c
│           │   ├── report.json
│           │   └── response_iteration0.md
│           └── run4
│               ├── Makefile
│               ├── latest_message
│               ├── message_send_at_iteration0.json
│               ├── reno_tsnym.c
│               ├── report.json
│               └── response_iteration0.md
└── RQ4
    └── Feedback1
        └── reno
            └── reno-throughtput-gpt-4o-mini-temp0.5-fb5-cot
                ├── run0
                │   ├── Makefile
                │   ├── latest_message
                │   ├── message_send_at_iteration0.json
                │   ├── reno_tcdrt.c
                │   ├── report.json
                │   └── response_iteration0.md
                ├── run1
                │   ├── Makefile
                │   ├── latest_message
                │   ├── message_send_at_iteration0.json
                │   ├── reno_twfvz.c
                │   ├── report.json
                │   └── response_iteration0.md
                ├── run2
                │   ├── Makefile
                │   ├── latest_message
                │   ├── message_send_at_iteration0.json
                │   ├── reno_tqcpz.c
                │   ├── report.json
                │   └── response_iteration0.md
                ├── run3
                │   ├── Makefile
                │   ├── latest_message
                │   ├── message_send_at_iteration0.json
                │   ├── reno_tqhrx.c
                │   ├── report.json
                │   └── response_iteration0.md
                └── run4
                    ├── Makefile
                    ├── latest_message
                    ├── message_send_at_iteration0.json
                    ├── reno_tsnym.c
                    ├── report.json
                    └── response_iteration0.md

```