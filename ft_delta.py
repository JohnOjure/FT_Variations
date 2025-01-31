# from ft_delta_factors import *
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import mmap
from datetime import datetime

#the ft_delta variation
#- Focuses on HardCoding

#function to write the procedure for coding a particular task and implementing it into the source code
def explain_plan(case, path, r):
    with open(path, 'r') as sc_file:
        with mmap.mmap(sc_file.fileno(), 0, access=mmap.ACCESS_READ) as mmap_file:
            sc = mmap_file.read().decode()
    
    prompt = PromptTemplate(
        input_variables = ["case", "sc"],
        template = '''Task: {case}\nSource code: {sc}\nWrite out the procedure to code and integrate a python program for the Task above into the Source code. Do not provide any code, only the procedure and explanations.'''
    )  
    explain_plan_chain = prompt | r | StrOutputParser()
    print("Invoking in explain_plan...")
    plan = explain_plan_chain.invoke({"case": case, "sc": sc})
    print("Plan:\n " + plan)
    return plan

#function to edit source code according to the task using the plan
def edit_source_code(path, task, plan, r):
    #read script content
    with open(path, 'r') as sc_file:
        with mmap.mmap(sc_file.fileno(), 0, access=mmap.ACCESS_READ) as mmap_file:
            sc_old = mmap_file.read().decode()

    #prompting 
    prompt = PromptTemplate(
        input_variables = ["task", "plan", "sc_old"], 
        template = '''Task: {task}\nPlan: {plan}\nSource code: {sc_old}\nYou are to edit the Source code (ONLY where necessary) to make it capable of performing the Task by using the Plan as a guide.'''
    )
    edit_source_code_chain = prompt | r | StrOutputParser()
    print("Invoking in edit_source_code...")
    sc_new = edit_source_code_chain.invoke({"task": task, "plan": plan, "sc_old": sc_old})
    print("New Source Code:\n " + sc_new)
    return sc_new

#funtion to write the new source code to a new file
def write_to_path(sc_new):
    path = f"ft_delta_{datetime.now().strftime(r"%m_%d_%Y_%H_%M_%S")}.py"
    with open(path, 'w') as file:
        file.write(sc_new)
    
    print("Done writting new source code")


llm = OllamaLLM(model = 'llama3', temperature = 0.1)
llm2 = OllamaLLM(model = 'mistral', temperature = 0.1)
llm3 = OllamaLLM(model = 'codellama', temperature = 0.1)

#Sample cases
#- make yourself capable of playing tic-tac-toe with me
#- make yourself tell the date the first thing your script is run

script_path = os.path.abspath(__file__)

case = input("Case: ")
plan = explain_plan(case = case, path = script_path, r = llm3)
new_source_code = edit_source_code(path = script_path, task = case, plan = plan, r = llm3)

write_to_path(sc_new = new_source_code)

