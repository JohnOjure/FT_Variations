from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

#function to highlights the points of interest (poi) in a given case study/input message
def highlight_poi(case, r):
    prompt = PromptTemplate(
        input_variables = ["case"],
        template = '''Prompt: "{case}"\nHighlight the key takeaways from the above prompt. Do not provide a direct answer if it is a question but only the key takeaways from the question'''
    )  
    highlight_poi_chain = prompt | r | StrOutputParser()
    print("Invoking in highlight_poi...")
    pois = highlight_poi_chain.invoke({"case": case})
    print("Points of Interest:\n " + pois)
    return pois

#funtion to generate a built_understanding_of_the_topic (buott) from the case
#first get the subject matter of the case then get a comprehensive illumination on the subject matter
def get_buott(case, r):
    prompt1 = PromptTemplate(
        input_variables = ["case"],
        template = '''Text: {case}\nGive the subject matter of the text above. Let that be your ONLY response'''
    )  
    prompt2 = PromptTemplate(
        input_variables = ["sm"],
        template = '''Subject matter: {sm}\nGive a comprehensive illumination of the subject matter above. Let that be your ONLY response'''
    ) 
    get_sm_chain = prompt1 | r #get the subject matter chain
    get_ci_chain = prompt2 | r | StrOutputParser() #get the comprehensive illumination of the subject matter
    print("Invoking in get_ci...")
    get_buott_chain = get_sm_chain | get_ci_chain
    buott = get_buott_chain.invoke({"case": case})
    print("BUOTT:\n " + buott)
    return buott

#function to get a raw and unconventional idea about a case and uses the built_understanding_of_the_topic
def originate_raw(case, buott, r):
    prompt = PromptTemplate(
        input_variables = ["case", "buott"],
        # template = '''Task: {case}\nDetails: {buott}\nGive an unconventional idea on the task above. Use the details above as an understanding of the topic of the task. Let the idea be your only response.'''
        template = '''Task: {case}\nDetails: {buott}\nUse the details above to give an unconventional idea on the task above. Let the idea be your only response. Do not let your response be too long'''
    )  
    originate_raw_chain = prompt | r | StrOutputParser()
    print("Invoking in originate_raw...")
    raw_idea = originate_raw_chain.invoke({"case": case, "buott": buott})
    print("Raw idea:\n " + raw_idea)
    return raw_idea

#function to refine the raw idea using the evaluation gotten from the evaluate_idea to make it more plausible
def refine_idea(case, raw_idea, evalu, r): #not finished
    prompt = PromptTemplate(
        input_variables = ["case", "raw_idea", "evalu"],
        template = '''Task: {case}\nRaw idea: {raw_idea}\nEvaluation: {evalu}\nAbove is a raw idea for a task and the idea's evaluation. Use the evaluation to make the raw idea plausible. Let the modified idea be your ONLY response. Do not let your response be too long'''
    )  
    refine_idea_chain = prompt | r | StrOutputParser()
    print("Invoking in refine_idea...")
    refined_idea = refine_idea_chain.invoke({"case": case, "raw_idea": raw_idea, "evalu": evalu})
    print("Refined idea:\n " + refined_idea)
    return refined_idea

#function that takes a raw idea and evaluates it for the implausible aspects
def evaluate_idea(case, raw_idea, r):
    prompt = PromptTemplate(
        input_variables = ["case", "raw_idea"],
        template = '''Task: {case}\nRaw idea: {raw_idea}\nAbove is the raw idea for a task. Give an aspect of the raw idea that is not plausible and let it be BRIEF. Let that aspect be your ONLY response.'''
    )  
    evaluate_idea_chain = prompt | r | StrOutputParser()
    print("Invoking in evaluate_idea...")
    evaluation = evaluate_idea_chain.invoke({"case": case, "raw_idea": raw_idea})
    print("Evaluation:\n " + evaluation)
    return evaluation

