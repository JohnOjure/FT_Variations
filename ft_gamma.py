# from ft_gamma_factors import *
from ft_gamma_factors_2 import *
from langchain_ollama import OllamaLLM
import json
import re

#the ft_beta variation
#- Focuses on Introspection

llm = OllamaLLM(model = 'llama3', temperature = 0.5)
llm2 = OllamaLLM(model = 'mistral', temperature = 0.5)

case = input("Case: ")
tone = input("Tone: ")
preplan = input("Preplan?: (y/n)")

tone = "neutral" if tone == '' else tone
preplan = "yes" if preplan == 'y' else "no"
print(f"Set tone of discussion: {tone}")

#sample cases
#- democracy
#- self-awareness
#- An idea for how LLMs can learn new things: To enable Large Language Models (LLMs) to learn new skills, concepts, and things effectively, a hybrid approach of "reverse mentorship" and continual learning can be implemented. In this method, LLMs are presented with a series of increasingly complex questions or prompts that require problem-solving based on the knowledge they have been trained on. Human evaluators consistently assess the model's performance by comparing its responses to high-quality reference answers, providing feedback in the form of rewards or penalties. This feedback serves as a guide for further training, allowing the model to refine its responses and improve its understanding of the subject matter.
#- An idea for how LLMs can learn new things: To enable Large Language Models (LLMs) to learn new skills, concepts, and things effectively, a hybrid approach of "reverse mentorship" and continual learning can be implemented. In this method, LLMs are presented with a series of increasingly complex questions or prompts that require problem-solving based on the knowledge they have been trained on. Human evaluators consistently assess the model's performance by comparing its responses to high-quality reference answers, providing feedback in the form of rewards or penalties. This feedback serves as a guide for further training, allowing the model to refine its responses and improve its understanding of the subject matter. How would one go about all the various aspects of the coding and implementation of this idea?
#- Solve 2x^3 + 4x^2 = 3
#- How many 'r's are in strawberry?

#sample tones
#- critical(analytical)
#- conflicting
#- deliberative
#- inquisitive
#- deeply critical(analytical) and solution-oriented

#---Continue_notes---
#Using the sii_technique only for devising a plan for the MoD for now. Will extend it and allow it to be used dynamically
#Test the system using the whispers using the strategy using the sii but go through the code one more time
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
discussion_history = ""
discussion_history_with_whispers = ""
remark_from_r1 = ""
remark_from_r2 = ""
nRsoD = 6 #number of Rounds of Discussion
whisper_delay = 2 #whisper after every 'n' round(s)
sii = SII(llm = llm, llm2 = llm2)

if preplan == "yes":
    #determine if a strategy/plan is needed to guide the discussion
    strategy_is_needed, instruction = use_strategy(case = case, r = llm)
    if strategy_is_needed == "Yes":
        strategy = sii(case = instruction, tone = "methodical, analytical, and objective", nRsoD = 4, whisper_delay = 1)
    else:
        strategy = None
else:
    strategy = None

#looping for the rounds of discussion
for _ in range (1, nRsoD+1):
    if _ % whisper_delay == 0: #get whispers after a specific nRsoD
        whisper = whisper_tweak(case = case, history = discussion_history, strategy = strategy, r = llm)
        #whispering is done to ensure the discussion follows the plan (if there's one), is objective and doesn't go off the rails. It acts as the system's self-correction mechanism
    else:
        whisper = None

    is_first_round = False if _ > 1 else True #determine if it's the first round of discussion
    print(f"---New Round of Discussion---({str(_)}/{str(nRsoD)})")
    
    #get the remarks from r1 and r2
    remark_from_r1, remark_from_r1_string = get_remark_from_r1(case = case, mfr2 = remark_from_r2, history = discussion_history, first_round = is_first_round, tone = tone, whisper = whisper, r = llm)
    remark_from_r2, remark_from_r2_string = get_remark_from_r2(case = case, mfr1 = remark_from_r1, history = discussion_history, first_round = is_first_round, tone = tone, whisper = None, r = llm2)

    #update the discussion history
    discussion_history = discussion_history + f"{remark_from_r1_string}\n{remark_from_r2_string}\n"
    discussion_history_with_whispers = discussion_history_with_whispers + "\n\n\x1B[3m" + f"Whisper: {whisper}" + "\x1B[0m\n\n" + f"{remark_from_r1_string}\n\n{remark_from_r2_string}\n\n" if whisper != None else discussion_history_with_whispers + f"{remark_from_r1_string}\n\n{remark_from_r2_string}\n\n"

#after the rounds of discussion, draw a conclusion from the discussion_history that will serve as an EO
ending_opinion = draw_conlusion(case = case, history = discussion_history, r = llm)

print(f"Discussion History:\n{discussion_history}\n\n")
print(f"Discussion History with whispers:\n{discussion_history_with_whispers}\n\n")

print("End")
