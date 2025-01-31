from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

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
#last rounds of discussion and give a final opinion/thought--*

#Stuff considering to do:
#   - Give each r-unit a specific role
#   - Muli-r-unit architecture
#   - Pass only discussion_history as context for next introspect--*
#   - Temporary instructions--*
#   - Use discussion_history to provide an EO--*
#   - Strategies

#implement the strategy stuff into the whispers somehow--*. When that is done, update the code in the sii class

#function that gets the remark of the first assessor
def get_remark_from_r1(case, mfr2, history, first_round, tone, whisper, r):
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
        if whisper != None: #if there's a whisper, use it
            print("\x1B[3m" + "Received whisper" + "\x1B[0m")
            prompt = PromptTemplate(
                input_variables = ["case", "history", "tone", "whisper"],
                template = '''Matter of discussion: {case}\nDiscussion history: {history}\nDirective: {whisper}\nYou are an independent assessor (R1) and you are engaged in a discussion with another assessor (R2). Above is the matter of discussion and discussion history for context understanding. The tone of the discussion is {tone}. Give your own remark on the matter of discussion FOLLOWING the discussion history. Consider the directive above when generating your remark. Let the remark be your ONLY response.'''
            )  
            r1_chain = prompt | r | StrOutputParser()
            print("Invoking in r1...")
            remark = r1_chain.invoke({"case": case, "history": history, "tone": tone, "whisper": whisper})
            remark_string = f"R1: {remark}"
            print("R1: " + remark + "\n")
            return remark, remark_string
        else:        
            prompt = PromptTemplate(
                input_variables = ["case", "history", "tone"],
                template = '''Matter of discussion: {case}\nDiscussion history: {history}\nYou are an independent assessor (R1) and you are engaged in a discussion with another assessor (R2). Above is the matter of discussion and discussion history for context understanding. The tone of the discussion is {tone}. Give your own remark on the matter of discussion FOLLOWING the discussion history. Let the remark be your ONLY response.'''
            )  
            r1_chain = prompt | r | StrOutputParser()
            print("Invoking in r1...")
            remark = r1_chain.invoke({"case": case, "history": history, "tone": tone})
            remark_string = f"R1: {remark}"
            print("R1: " + remark + "\n")
            return remark, remark_string   

#function that gets the remark of the second assessor
def get_remark_from_r2(case, mfr1, history, first_round, tone, whisper, r):
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
        if whisper != None: #if there's a whisper, use it
            print("\x1B[3m" + "Received whisper" + "\x1B[0m")
            prompt = PromptTemplate(
                input_variables = ["case", "history", "tone", "whisper"],
                template = '''Matter of discussion: {case}\nDiscussion history: {history}\nDirective: {whisper}\nYou are an independent assessor (R1) and you are engaged in a discussion with another assessor (R2). Above is the matter of discussion and discussion history for context understanding. The tone of the discussion is {tone}. Give your own remark on the matter of discussion FOLLOWING the discussion history. Consider the directive above when generating your remark. Let the remark be your ONLY response.'''
            )  
            r2_chain = prompt | r | StrOutputParser()
            print("Invoking in r2...")
            remark = r2_chain.invoke({"case": case, "history": history, "tone": tone, "whisper": whisper})
            remark_string = f"R2: {remark}"
            print("R2: " + remark + "\n")
            return remark, remark_string
        else:
            prompt = PromptTemplate(
                input_variables = ["case", "history", "tone"],
                template = '''Matter of discussion: {case}\nDiscussion history: {history}\nYou are an independent assessor (R2) and you are engaged in a discussion with another assessor (R1). Above is the matter of discussion and discussion history for context understanding. The tone of the discussion is {tone}. Give your own remark on the matter of discussion FOLLOWING the discussion history. Let the remark be your ONLY response.'''
            )  
            r2_chain = prompt | r | StrOutputParser()
            print("Invoking in r2...")
            remark = r2_chain.invoke({"case": case, "history": history, "tone": tone})
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

#function that reviews discussion history against the input_case and then 'whispers' any instructions or tweaks
#that are needed to perform the task or that would be needed to change anything. Can be used as a form of autocorrection 
#may use it to suggest strategies
def whisper_tweak(case, history, strategy, r):
    if strategy != None:
        prompt = PromptTemplate(
            input_variables = ["case", "history", "strategy"],
            template = '''Matter of discussion: {case}\nDiscussion history: {history}\nPlan: {Plan}. Above is the matter of discussion, the discussion history of two independent assessors and the plan to guide the discussion. Your job is to review the discussion history and recommend any instructions that would guide the discussion towards tackling the matter of discussion. Use the plan when recommending these instructions. Let the recommended instruction(s) be your only response.'''
        )  
        whisper_tweak_chain = prompt | r | StrOutputParser()
        print("Invoking in whisper_tweak...")
        tweak = whisper_tweak_chain.invoke({"case": case, "history": history, "strategy": strategy})
        print("Whispered tweak: " + tweak)
        return tweak
    else:
        prompt = PromptTemplate(
            input_variables = ["case", "history"],
            template = '''Matter of discussion: {case}\nDiscussion history: {history}\nAbove is the matter of discussion and the discussion history of two independent assessors. Your job is to review the discussion history and recommend any instructions that would guide the discussion towards tackling the matter of discussion. For example: "Keep to the matter of discussion", "Stay on track and stop deviating", "This approach is incorrect, try this instead", "Stop saying the same things over and over again", e.t.c. Let the recommended instruction(s) be your only response.'''
        )  
        whisper_tweak_chain = prompt | r | StrOutputParser()
        print("Invoking in whisper_tweak...")
        tweak = whisper_tweak_chain.invoke({"case": case, "history": history})
        print("Whispered tweak: " + tweak)
        return tweak
#function that determines if a strategy or plan is needed to go about a particular task
def use_strategy(case, r):
    prompt = PromptTemplate(
        input_variables = ["case"],
        template = '''Matter of discussion: {case}\nAbove is a matter of discussion. You are to determine whether some planning or strategy is needed for the matter of discussion. If some planning or strategy is needed, let your ONLY response be Yes. If no planning or strategy is needed, let your ONLY response be No.'''
    )  
    use_strategy_chain = prompt | r | StrOutputParser()
    print("Invoking in use_strategy...")
    answer = use_strategy_chain.invoke({"case": case})
    print("Use strategy answer: " + answer)

    is_yes = re.match(r'^(Yes|yes)', answer.strip())
    answer = "Yes" if is_yes == True else "No"
    if answer == "Yes":
        prompt2 = PromptTemplate(
        input_variables = ["case"],
        template = '''Matter of discussion: {case}\nAbove is a matter of discussion. Write an instruction saying that a well thought out plan/strategy should be provided on how to go about what is contained in the matter of discussion. Emphasize that it is only the plan/strategy that is needed. Let the instruction you write be brief but concise. Let the instruction be your ONLY response.'''
    )  
        instruction_chain = prompt2 | r | StrOutputParser()
        print("Invoking instruction_chain...")
        instruction = instruction_chain.invoke({"case": case})
        print("Instruction to get strategy: " + instruction)
    else:
        instruction = None

    return answer, instruction

# a class for sub_introspection_instances
#yet to update the SII code to make it capable of calling SIIs on deeper levels
class SII:
    #initializing the variables for this paricular instance
    def __init__(self, llm, llm2):
        self.llm = llm
        self.llm2 = llm2

    def get_remark_from_r1_sii(self, case, mfr2, history, first_round, tone, whisper, r):
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
            if whisper != None: #if there's a whisper, use it
                print("\x1B[3m" + "Received whisper" + "\x1B[0m")
                prompt = PromptTemplate(
                    input_variables = ["case", "history", "tone", "whisper"],
                    template = '''Matter of discussion: {case}\nDiscussion history: {history}\nDirective: {whisper}\nYou are an independent assessor (R1) and you are engaged in a discussion with another assessor (R2). Above is the matter of discussion and discussion history for context understanding. The tone of the discussion is {tone}. Give your own remark on the matter of discussion FOLLOWING the discussion history. Consider the directive above when generating your remark. Let the remark be your ONLY response.'''
                )  
                r1_chain = prompt | r | StrOutputParser()
                print("Invoking in r1...")
                remark = r1_chain.invoke({"case": case, "history": history, "tone": tone, "whisper": whisper})
                remark_string = f"R1: {remark}"
                print("R1: " + remark + "\n")
                return remark, remark_string
            else:        
                prompt = PromptTemplate(
                    input_variables = ["case", "history", "tone"],
                    template = '''Matter of discussion: {case}\nDiscussion history: {history}\nYou are an independent assessor (R1) and you are engaged in a discussion with another assessor (R2). Above is the matter of discussion and discussion history for context understanding. The tone of the discussion is {tone}. Give your own remark on the matter of discussion FOLLOWING the discussion history. Let the remark be your ONLY response.'''
                )  
                r1_chain = prompt | r | StrOutputParser()
                print("Invoking in r1...")
                remark = r1_chain.invoke({"case": case, "history": history, "tone": tone})
                remark_string = f"R1: {remark}"
                print("R1: " + remark + "\n")
                return remark, remark_string   

    #function that gets the remark of the second assessor
    def get_remark_from_r2_sii(self, case, mfr1, history, first_round, tone, whisper, r):
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
            if whisper != None: #if there's a whisper, use it
                print("\x1B[3m" + "Received whisper" + "\x1B[0m")
                prompt = PromptTemplate(
                    input_variables = ["case", "history", "tone", "whisper"],
                    template = '''Matter of discussion: {case}\nDiscussion history: {history}\nDirective: {whisper}\nYou are an independent assessor (R1) and you are engaged in a discussion with another assessor (R2). Above is the matter of discussion and discussion history for context understanding. The tone of the discussion is {tone}. Give your own remark on the matter of discussion FOLLOWING the discussion history. Consider the directive above when generating your remark. Let the remark be your ONLY response.'''
                )  
                r2_chain = prompt | r | StrOutputParser()
                print("Invoking in r2...")
                remark = r2_chain.invoke({"case": case, "history": history, "tone": tone, "whisper": whisper})
                remark_string = f"R2: {remark}"
                print("R2: " + remark + "\n")
                return remark, remark_string
            else:
                prompt = PromptTemplate(
                    input_variables = ["case", "history", "tone"],
                    template = '''Matter of discussion: {case}\nDiscussion history: {history}\nYou are an independent assessor (R2) and you are engaged in a discussion with another assessor (R1). Above is the matter of discussion and discussion history for context understanding. The tone of the discussion is {tone}. Give your own remark on the matter of discussion FOLLOWING the discussion history. Let the remark be your ONLY response.'''
                )  
                r2_chain = prompt | r | StrOutputParser()
                print("Invoking in r2...")
                remark = r2_chain.invoke({"case": case, "history": history, "tone": tone})
                remark_string = f"R2: {remark}"
                print("R2: " + remark + "\n")
                return remark, remark_string   

    #function to evaluate the discussion history and draw a conclusion
    def draw_conlusion_sii(self, case, history, r):
        prompt = PromptTemplate(
            input_variables = ["case", "history"],
            template = '''Matter of discussion: {case}\nDiscussion history: {history}\nAbove is the matter of discussion and the discussion history. Review the discussion history and use it to draw a conclusion for the matter of discussion. Let the conclusion be your ONLY response.'''
        )  
        provide_eo_chain = prompt | r | StrOutputParser()
        print("Invoking in provide_eo...")
        eo = provide_eo_chain.invoke({"case": case, "history": history})
        print("Ending Opinion: " + eo)
        return eo

    #function that reviews discussion history against the input_case and then 'whispers' any instructions or tweaks
    #that are needed to perform the task or that would be needed to change anything. Can be used as a form of autocorrection 
    #may use it to suggest strategies
    def whisper_tweak_sii(self, case, history, r):
        prompt = PromptTemplate(
            input_variables = ["case", "history"],
            template = '''Matter of discussion: {case}\nDiscussion history: {history}\nAbove is the matter of discussion and the discussion history of two independent assessors. Your job is to review the discussion history and recommend any instructions that would guide the discussion towards tackling the matter of discussion. For example: "Keep to the matter of discussion", "Stay on track and stop deviating", "This approach is incorrect, try this instead", "Stop saying the same things over and over again", e.t.c. Let the recommended instruction(s) be your only response.'''
        )  
        whisper_tweak_chain = prompt | r | StrOutputParser()
        print("Invoking in whisper_tweak...")
        tweak = whisper_tweak_chain.invoke({"case": case, "history": history})
        print("Whispered tweak: " + tweak)
        return tweak

    def __call__(self, case, tone, nRsoD, whisper_delay): 
        print("--------------------------------------------------")
        print("------Entering a Sub-Instrospection-Instance------")
        tone = "neutral" if tone == '' else tone
        print(f"Set tone of discussion: {tone}")

        discussion_history = ""
        discussion_history_with_whispers = ""
        remark_from_r1 = ""
        remark_from_r2 = ""

        for _ in range (1, nRsoD+1):
            if _ % whisper_delay == 0: #get whispers after a specific nRsoD
                whisper = self.whisper_tweak_sii(case = case, history = discussion_history, r = self.llm)
            else:
                whisper = None

            is_first_round = False if _ > 1 else True #determine if it's the first round of discussion
            print(f"---New Round of Discussion---({str(_)}/{str(nRsoD)})")
            
            #get the remarks from r1 and r2
            remark_from_r1, remark_from_r1_string = self.get_remark_from_r1_sii(case = case, mfr2 = remark_from_r2, history = discussion_history, first_round = is_first_round, tone = tone, whisper = whisper, r = self.llm)
            remark_from_r2, remark_from_r2_string = self.get_remark_from_r2_sii(case = case, mfr1 = remark_from_r1, history = discussion_history, first_round = is_first_round, tone = tone, whisper = None, r = self.llm2)

            #update the discussion history
            discussion_history = discussion_history + f"{remark_from_r1_string}\n{remark_from_r2_string}\n"
            discussion_history_with_whispers = discussion_history_with_whispers + "\n\n\x1B[3m" + f"Whisper: {whisper}" + "\x1B[0m\n\n" + f"{remark_from_r1_string}\n\n{remark_from_r2_string}\n\n" if whisper != None else discussion_history_with_whispers + f"{remark_from_r1_string}\n\n{remark_from_r2_string}\n\n"

        ending_opinion = self.draw_conlusion_sii(case = case, history = discussion_history, r =self.llm)
        print("---------Exiting Sub-Instrospection-Instance---------")
        print("-----------------------------------------------------")
        return(ending_opinion)
