from ft_beta_factors import *
from langchain_ollama import OllamaLLM
import json
import re

#the ft_beta variation
# - Focuses on Origination

#sample cases
#- Rebuilding democracy from scratch to avoid the issues present in the current system
#- unlocking time travel
#- How LLMs can actually learn new skills, concepts and things
#- Combining self-assessment, forgetting curve, and meta-learning to enable LLMs learn completely new skills, concepts and things

#sample buotts
buott1 = "Quantum mechanics"
buott2 = "Core concept of democracy"
buott3 = "How humans learn new things"
buott4 = '''An idea for how LLMs can learn new things: To enable Large Language Models (LLMs) to learn new skills, concepts, and things effectively, a hybrid approach of "reverse mentorship" and continual learning can be implemented. In this method, LLMs are presented with a series of increasingly complex questions or prompts that require problem-solving based on the knowledge they have been trained on. Human evaluators consistently assess the model's performance by comparing its responses to high-quality reference answers, providing feedback in the form of rewards or penalties. This feedback serves as a guide for further training, allowing the model to refine its responses and improve its understanding of the subject matter.'''
buott5 = "Self-assessment, forgetting curve, and meta-learning in LLMs"

llm = OllamaLLM(model = 'llama3', temperature = 0.1)
llm2 = OllamaLLM(model = 'mistral', temperature = 0.1) #good for writing and rewriting

llms = [llm2, llm]
# llm_in_use = llm2 # continue and find a way to rotate it among the two llms
llm_counter = 0

case = input("Case: ")

pois_for_case = highlight_poi(case = case, r = llm)

buott_for_case = get_buott(case = buott3, r = llm) 

llm.temperature = 0.7
raw_idea = originate_raw(case = case, buott = buott_for_case, r = llm) #try with llm2
llm.temperature = 0.1

for _ in range(6):
    llm_in_use = llms[llm_counter%2]
    eval_analysis = evaluate_idea(case = case, raw_idea = raw_idea, r = llm)
    raw_idea = refine_idea(case = case, raw_idea = raw_idea, evalu = eval_analysis, r = llm_in_use)
    llm_counter+=1
    print("\n")


