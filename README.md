# Toward Non-Expert Customized Congestion Control, IEEE ICC'25
## NECC: Non-Expert Customized Congestion Control framework

**Enables non-expert users to easily model, implement, and deploy customized Congestion Control Algorithms (CCAs)[1]**

This repository contains the source code, experiment scripts, and prompts for the paper "Toward Non-Expert Customized Congestion Control" accepted by the 2025 IEEE International Conference on Communications (ICC).
[Paper Link](p3288-zhang.pdf)

[1]**customized Congestion Control Algorithms (CCAs)**: The CCAs that are designed to meet the specific requirements of certain users. They differ from general congestion control goals, such as fairly allocating bandwidth among competing flows, maximizing network utilization, and avoiding network congestion.

## Outline

1. [Repo Structure](#repo-structure)

1. [Design](#design)

1. [Reproduction](#reproduction)

1. [Acknowledgement](#acknowledgement)


## Repo Structure

1. ```NECC/Prompts``` Prompts
2. ```NECC/TCP_CCAs_in_BPF``` TCP CCA source code in BPF format
3. ```NECC/Mininet_testbed``` Evaluation code
4. ```NECC/Generation``` Prompt design, save results, ...

## Design

1. [Prompts](#prompts)

1. [TCP CCA source code in BPF format](#tcp-cca-source-code-in-bpf-format)

1. [Makefile](#makefile)


### Prompts:

* 0-shot prompts to output satisfying CCA code
  
Location: ```Prompts/system_prompt```

* Chain-of-Thought prompts to output satisfying CCA code
  
Location: ```Prompts/cot_system_prompt```

* Customized throughput requirement and safety requirements
  
Location: ```Prompts/throughput```

* Related Linux network stack code reference
  
Location: ```Prompts/gen_variable```

### TCP CCA source code in BPF format:

* bpf_cubic.c
  
Location: ```TCP_CCAs_in_BPF/bpf_cubic/bpf_cubic.c``` 

Modified from Linux [/tools/testing/selftests/bpf/progs/bpf_cubic.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/tools/testing/selftests/bpf/progs/bpf_cubic.c)

* bpf_reno.c
  
Location: ```TCP_CCAs_in_BPF/bpf_reno/bpf_reno.c```

Written with reference to bpf_cubic.c format and [/net/ipv4/tcp_cong.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/net/ipv4/tcp_cong.c)

* bpf_vegas.c
  
Location: ```TCP_CCAs_in_BPF/bpf_vegas/bpf_vegas.c```

Written with reference to bpf_cubic.c format and [/net/ipv4/tcp_vegas.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/net/ipv4/tcp_vegas.c)

* bpf_illinois.c
  
Location: ```TCP_CCAs_in_BPF/bpf_illinois/bpf_illinois.c```

Written with reference to bpf_cubic.c format and [/net/ipv4/tcp_illinois.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/net/ipv4/tcp_illinois.c)

* BPF TCP CC compile headers
  
Location: ```TCP_CCAs_in_BPF/headers/bpf_tracing_net.h```

Modified from [/tools/testing/selftests/bpf/progs/bpf_tracing_net.h](
https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/tools/testing/selftests/bpf/progs/bpf_tracing_net.h)

* BPF TCP CC calculation headers
  
Location: ```TCP_CCAs_in_BPF/headers/cal.h```

Implement division function (mydiv) without asm, and define macro do_div to mydiv.

Borrow div64_u64, clamp, min, max, before, after macro definitions from [/tools/testing/selftests/bpf/progs/bpf_cubic.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/tools/testing/selftests/bpf/progs/bpf_cubic.c)


* Reference:

https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/tools/testing/selftests/bpf/progs/bpf_cubic.c
https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/tools/testing/selftests/bpf/progs/bpf_dctcp.c
https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/tools/testing/selftests/bpf/progs/bpf_cc_cubic.c
https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/tools/testing/selftests/bpf/progs/tcp_ca_kfunc.c
 https://lore.kernel.org/bpf/20240322191433.4133280-2-martin.lau@linux.dev/

### Makefile

Template in Python

```python
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
```

Derived from [/tools/testing/selftests/bpf/Makefile](
https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/tools/testing/selftests/bpf/Makefile)

BPF system register operation Reference:
https://lpc.events/event/7/contributions/687/attachments/537/1262/BPF_network_tcp-cc-hdr-sk-stg_LPC_2020.pdf

## Reproduction

1. [Requirement Modeling](#requirement-modeling)

1. [Clone the repo](#clone-the-repo)

1. [Install required packages](#install-required-packages)

1. [Run the code](#run-the-code)

### Requirement Modeling

Prompt design 

```
You are an assistant to help users to model their networking requirements to code instructions.
You will need to collect the following information by asking the user one by one:
1. {Reuirement}: What is the requirement of the network?
2. {Upload speed}: What is your Internet's upload speed? In Mbps unit.

Then, your tasks are:
1. calculate the {Reuirement} to {throughput} with Mbps unit in numerical value without any explanation. Use the most common assumption during the calculation.
2. calculate 80% of {Upload speed} as {Max Upload speed}


Then, output in the following format:
"
The requirement is: 
If the overall packet loss rate, measured from the start of the connection to the current time, is 5% or higher, adjust the throughput using the original logic provided in the source code or references. If the packet loss rate is less than 5%, ensure that the instantaneous throughput is always at least a minimum of {throughput} Mbps but does not exceed a maximum of {Max Upload speed} Mbps.
"
```

### Clone the repo

```
$ sudo apt update; sudo apt install -y git 
$ git clone https://github.com/zmrui/NECC
```

### Install required packages

The steps were tested on Ubuntu 22.04

1. [Install Bpftool](#1-install-bpftool)
2. [Install Mininet](#2-install-mininet)
3. [Install Clang](#3-install-clang)
4. Install Model Providers' API
5. [(Optional) Dump vmlinux.h of current machine](#5-optional-dump-vmlinuxh-of-current-system)

#### 1. Install Bpftool

See bpftool for more detailes [https://github.com/libbpf/bpftool](https://github.com/libbpf/bpftool)

This is to install bpftool, ```libelf``` and ```zlib```

```
$ sudo apt install -y zip bison build-essential cmake flex git libedit-dev libllvm14 llvm-14-dev libclang-14-dev python3 zlib1g-dev libelf-dev libfl-dev python3-setuptools liblzma-dev libdebuginfod-dev arping netperf iperf iperf3 python3-pip
```

```
$ git clone --recurse-submodules https://github.com/libbpf/bpftool.git

$ cd bpftool
$ cd src
$ make install
```


#### 2. Install Mininet

See Mininet documents at [https://mininet.org/download/#option-2-native-installation-from-source](https://mininet.org/download/#option-2-native-installation-from-source)

```
$ git clone https://github.com/mininet/mininet
$ cd mininet
$ git tag  # list available versions
$ git checkout -b mininet-2.3.0 2.3.0 
$ cd ..
$ sed -i 's|git://|https://|g' mininet/util/install.sh
$ mininet/util/install.sh -a
```

#### 3. Install Clang

Clang is needed to build BPF targets.

```
sudo apt install clang
```


#### 4. Install Model Providers' API


#### 5. (Optional) Dump vmlinux.h of current system

The ```vmlinux.h``` in this repo is dumped from an Ubuntu 22.04 with kernel v6.11.1, and may not be compatible with other systems or kernels.

```
bpftool btf dump file /sys/kernel/btf/vmlinux format c > TCP_CCAs_in_BPF/headers/vmlinux.h
```

### Run the code

Configurations variables:
* Configure API key(s) in ```Generation/utils/clients.py``` OR follow their Documents
* Configure your username as ```USER``` variable in ```Generation/utils/config.py```
* Configure the cloned repo's absolute path as  ```ROOTDIR``` variable in ```Generation/utils/config.py``` (Used to change back the result directory permissions after execuation)

Next, see Execution.md

## Acknowledgement

Part of Mininet emulation code (```NECC/Mininet_testbed/core```) is implemented based on "Giacomoni, Luca; Parisis, George (2024). Code for Reinforcement Learning-based Congestion Control: A Systematic Evaluation of Fairness, Efficiency and Responsiveness. University of Sussex. Software. [https://doi.org/10.25377/sussex.24978162.v2](https://doi.org/10.25377/sussex.24978162.v2) " with customized modifications. Thanks to authors for their open-source codes!

### Cite

If you find this work helpful, please consider citing our paper presented at IEEE ICC'25
```
Mingrui Zhang, Hamid Bagheri, and Lisong Xu, “Toward Non-Expert Customized Congestion Control”, in the IEEE International Conference on Communications (ICC), Montreal, Canada, June 2025, pp. 3288-3294.
```


### License

[GNU GENERAL PUBLIC LICENSE](https://github.com/zmrui/NECC?tab=GPL-2.0-1-ov-file)

**Kernel**: ```SPDX-License-Identifier: GPL-2.0 WITH Linux-syscall-note```
