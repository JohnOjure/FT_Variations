from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

#consider using different temperatures for the two llms

#later on, there will be another factor that will be called at the end of a specified
#number of rounds_of_discussion. This factor will evalute the disscusion_history and 
#determine if r1 and r2 have reached a consensus on any particular thing or aspect of
#the conversation. If there is, it will form a 'belief' from what r1 and r2 had a consensus on.
#This 'belief' is used and affects future discussions in the particular domain the belief was
#gotten from.
#A group of beliefs from a particular domain are put in a belief_list which is used to guide 
#introspection in that domain

#Also, there will be a function that will take the discussion history, consider the 
#last rounds of discussion and give a final opinion/thought

#Stuff considering to do:
#   - Give each r-unit a specific role
#   - Muli-r-unit architecture
#   - Pass only discussion_history as context for next introspect
#   - Temporary instructions
#   - Use discussion_history to provide an EO

#function that gets the remark of the first assessor
def get_remark_from_r1(case, mfr2, history, first_round, tone, r):
    if first_round == True: #first round starting from r1  
        print("First round from r1")  
        prompt = PromptTemplate(
            input_variables = ["case", "tone"],
            template = '''Matter of discussion: {case}\nYou are an independent assessor and you are engaged in a discussion with another assessor. The tone of the discussion is {tone}. Give your own remark concerning the matter of discussion above. Let the remark be your ONLY response.'''
        )  
        r1_chain = prompt | r | StrOutputParser()
        print("Invoking in r1...")
        remark = r1_chain.invoke({"case": case, "tone": tone})
        remark_string = f"R1: {remark}"
        print("R1: " + remark + "\n")
        return remark, remark_string 
    else: #r1 and r2 have gone one round already so a history list exists
        prompt = PromptTemplate(
            input_variables = ["case", "mfr2", "history", "tone"],
            template = '''Matter of discussion: {case}\nDiscussion history: {history}\nRemark from R2: {mfr2}\nYou are an independent assessor (R1) and you are engaged in a discussion with another assessor (R2). Above is the matter of discussion and discussion history for context understanding. The tone of the discussion is {tone}. Give your own remark to R2's remark. Let the remark be your ONLY response.'''
        )  
        r1_chain = prompt | r | StrOutputParser()
        print("Invoking in r1...")
        remark = r1_chain.invoke({"case": case, "mfr2": mfr2, "history": history, "tone": tone})
        remark_string = f"R1: {remark}"
        print("R1: " + remark + "\n")
        return remark, remark_string   

#function that gets the remark of the second assessor
def get_remark_from_r2(case, mfr1, history, first_round, tone, r):
    if first_round == True: #first round starting from r1 and has gotten to r2
        print("First round from r2")   
        prompt = PromptTemplate(
            input_variables = ["case", "mfr1", "tone"],
            template = '''Matter of discussion: {case}\nRemark from R1: {mfr1}\nYou are an independent assessor and you are engaged in a discussion with another assessor (R1). Above is the matter of discussion for context understanding. The tone of the discussion is {tone}. Give your own remark to R1's remark. Let the remark be your ONLY response.'''
        )  
        r2_chain = prompt | r | StrOutputParser()
        print("Invoking in r2...")
        remark = r2_chain.invoke({"case": case, "mfr1": mfr1, "tone": tone})
        remark_string = f"R2: {remark}"
        print("R2: " + remark + "\n")
        return remark, remark_string 
    else: #r1 and r2 have gone one round already so a history list exists
        prompt = PromptTemplate(
            input_variables = ["case", "mfr1", "history", "tone"],
            template = '''Matter of discussion: {case}\nDiscussion history: {history}\nRemark from R1: {mfr1}\nYou are an independent assessor (R2) and you are engaged in a discussion with another assessor (R1). Above is the matter of discussion and discussion history for context understanding. The tone of the discussion is {tone}. Give your own remark to R1's remark. Let the remark be your ONLY response.'''
        )  
        r2_chain = prompt | r | StrOutputParser()
        print("Invoking in r1...")
        remark = r2_chain.invoke({"case": case, "mfr1": mfr1, "history": history, "tone": tone})
        remark_string = f"R2: {remark}"
        print("R2: " + remark + "\n")
        return remark, remark_string   

#function to evaluate the discussion history and draw a conclusion
def draw_conlusion(case, history, r):
    prompt = PromptTemplate(
        input_variables = ["case", "history"],
        template = '''Matter of discussion: {case}\nDiscussion history: {history}\nAbove is the matter of discussion and the discussion history. Review the discussion history and use it to draw a conclusion for the matter of discussion. Let the conclusion be your ONLY response.'''
    )  
    provide_eo_chain = prompt | r | StrOutputParser()
    print("Invoking in provide_eo...")
    eo = provide_eo_chain.invoke({"case": case, "history": history})
    print("Ending Opinion: " + eo)
    return eo
