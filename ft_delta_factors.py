from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import mmap
from datetime import datetime

#for the explain plan, probably pass current source code to it and ask it to give a plan on how to
#go about implementing the changes in the source code or the task

#add evaluation of code too

#maybe write code first then integrate it with SC later

#Task: {task}\nPlan: {plan}\nSource code: {sc}\nEdit the source code to make it capable of performing the task above using the Plan

# template = '''Task: {case}\nSource code: {sc}\nWrite out the procedure to code a proficient python program for the task above. Do not provide the code for the task itself but just the procedure and explanations'''
    
    #     template = '''Task: {task}\nPlan: {plan}\nSource code: {sc_old}\nYou are to:
    #     - Write efficient python code for the Task above using the Plan as a guide.
    #     - Integrate the code with Source code above by adding to it/ modifying it ONLY where necessary.
    #     - Ensure you put comments where necessary.
    #     - Return the the edited source code as your ONLY response.
    #     - Do not let your response contain any other explanations or text other than the code itself.'''
    # ) 
#----------------------------------------------------------------------------------------------------------------------------------------------

#function to write the procedure for coding a particular task
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


    

        
