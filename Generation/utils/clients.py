from openai import OpenAI
import os
import json
import Generation.utils.util
import Generation.utils.config

MAXTOKENS_ANTHROPIC = 8192
MAXTOKENS_OPENAI = 16384

openai_client = OpenAI(
    api_key="sk-proj-",
)

import anthropic
anthropic_client = anthropic.Anthropic(
    api_key="sk-ant-",
)


anthropic_system_content = anthropic.NOT_GIVEN
openai_system_content = None

def anthropic_message(msg,temperature,model):
    global anthropic_system_content
    message = anthropic_client.messages.create(
    model=model,
    system=anthropic_system_content,
    temperature=temperature,
    max_tokens=MAXTOKENS_ANTHROPIC,
    extra_headers={"anthropic-beta":"max-tokens-3-5-sonnet-2024-07-15"},
    messages=msg
)
    response_content = message.content[0].text

    response_item = {}
    response_item["role"] = "assistant"
    response_item["content"] = response_content
    msg.append(response_item)
    return(response_content,msg)

def openai_message(msg,temperature,model):
    chat_completion = openai_client.chat.completions.create(
    model=model,
    temperature=temperature,
    messages=msg,
    max_tokens=MAXTOKENS_OPENAI
)
    response_content = chat_completion.choices[0].message.content

    response_item = {}
    response_item["role"] = "assistant"
    response_item["content"] = response_content

    msg.append(response_item)
    return(response_content,msg)


def init_openai_message(system_content):
    global openai_system_content 
    openai_system_content = system_content
    return [
        {"role": "system", "content": system_content},
    ]

def init_anthropic_message(system_content):
    global anthropic_system_content 
    anthropic_system_content = system_content
    return []

def append_message(msg,role,content):
    item = {}
    item["role"] = role
    item["content"] = content
    msg.append(
        item
    )
    return msg

class LLM_CLIENT:
    def __init__(self,model:str,result_folder:str,temperature:int,strategy='fullref'):
        self.client = None
        self.model = model
        self.message = None
        self.result_folder=result_folder
        self.strategy=strategy
        self.temperature = temperature
        if "gpt" in model or "o1" in model:
            self.family = "OpenAI"
            self.client = openai_client
        elif "claude" in model:
            self.family = "Anthropic"
            self.client = anthropic_client

    def init_message(self,prompt_folder, cca_path,requirement,pe):
        coderef, req, sysmeg = Generation.utils.util.load_message_direct(prompt_folder=prompt_folder, cca_path=cca_path,requirement=requirement,pe=pe)
        
        self.req = req
        self.sysmeg = sysmeg+coderef
        print("# loaded initial messages content")
    
    def load_message_history(self,prompt_folder, cca_path,requiremenm,pe):
        self.init_message(prompt_folder, cca_path,requiremenm,pe=pe)
        with open(os.path.join(os.getcwd(),self.result_folder,"latest_message"),"r") as f:
                self.message = json.loads(f.read())

    def init_system_message(self):
        systemmessage = self.sysmeg
        if self.family == "OpenAI":
            self.message = [
                {"role": "system", "content": systemmessage},
            ]
        elif self.family == "Anthropic":
            self.anthropic_system_content = systemmessage
            self.message = []
        print("# initialized system messages")
    def reload_system_message(self):
        systemmessage = self.sysmeg
        if self.family == "OpenAI":
            pass
        elif self.family == "Anthropic":
            self.anthropic_system_content = systemmessage
            
    def append_message(self,role,content):
        item = {}
        item["role"] = role
        item["content"] = content
        self.message.append(item)
        print("# new message appended")
    def pop_message(self):
        return self.message.pop()
    def push_message(self,item):
        self.message.append(item)
    def send_revision_messages_no_save(self,messagedict):
        response_content = None
        print("# Begin message sending")
        if self.family == "OpenAI":
            chat_completion = openai_client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messagedict,
            max_tokens=MAXTOKENS_OPENAI
        )
            print("# Message sent")
            response_content = chat_completion.choices[0].message.content
            response_item = {}
            response_item["role"] = "assistant"
            response_item["content"] = response_content
        elif self.family == "Anthropic":
            message = anthropic_client.messages.create(
            model=self.model,
            system=self.anthropic_system_content,
            temperature=self.temperature,
            max_tokens=MAXTOKENS_ANTHROPIC,
            extra_headers={"anthropic-beta":"max-tokens-3-5-sonnet-2024-07-15"},
            messages=messagedict
        )
            print("# Message sent")
            response_content = message.content[0].text
            response_item = {}
            response_item["role"] = "assistant"
            response_item["content"] = response_content
        else:
            pass

        self.last_assistant_result = response_item
        self.latest_response_content = response_content
        print("# Response get")
        return response_content
    def send_messages_no_save(self):
        response_content = None
        print("# Begin message sending")
        if self.family == "OpenAI":
            chat_completion = openai_client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=self.message,
            max_tokens=MAXTOKENS_OPENAI
        )
            print("# Message sent")
            response_content = chat_completion.choices[0].message.content
            response_item = {}
            response_item["role"] = "assistant"
            response_item["content"] = response_content
        elif self.family == "Anthropic":
            message = anthropic_client.messages.create(
            model=self.model,
            system=self.anthropic_system_content,
            temperature=self.temperature,
            max_tokens=MAXTOKENS_ANTHROPIC,
            extra_headers={"anthropic-beta":"max-tokens-3-5-sonnet-2024-07-15"},
            messages=self.message
        )
            print("# Message sent")
            response_content = message.content[0].text
            response_item = {}
            response_item["role"] = "assistant"
            response_item["content"] = response_content
        else:
            pass

        self.last_assistant_result = response_item
        self.latest_response_content = response_content
        print("# Response get")
        return response_content
    def save_last_assistant_result_to_message_history(self):
        self.message.append(self.last_assistant_result)

    def save_result_c_file(self,savename):
        
        with open(os.path.join(os.getcwd(),self.result_folder,savename+".c"),"w") as f:
            f.write(self.refined_response)

    def save_message_history(self,filename="latest_message"):
        with open(os.path.join(os.getcwd(),self.result_folder,filename),"w") as f:
            json_string = json.dumps(self.message, indent=4)  
            f.write(json_string)
        print("# Message history and result saved")
    def refine_response(self):
        self.refined_response = self.latest_response_content
    def refine_c_code(self):
        print("# Try to remove unrelated content in response")
        originalcode = self.refined_response
        begin_index = originalcode.index(Generation.utils.config.begin_flag)
        end_index = originalcode.index(Generation.utils.config.end_flag)
        pure_code = originalcode[begin_index:end_index]
        pure_code = pure_code.replace(Generation.utils.config.begin_flag,'')
        pure_code = pure_code.replace(Generation.utils.config.end_flag,'')
        self.refined_response = pure_code
    def change_cca_name(self,cca:str,newname):
        oldname = "bpf_"+cca
        self.refined_response = self.refined_response.replace(oldname,newname)
