from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re

#template = '''Input: {the_input}\nTentative output: {eo}\n Compare the tentative output against the input and determine if there something wrong with the tentative output. If there is something wrong, describe what the issue is. If there is nothing wrong, let your response be "No". '''

#function to highlights the points of interest (poi) in a given case study/input message
def highlight_poi(case, r):
    prompt = PromptTemplate(
        input_variables = ["case"],
        template = '''Highlight the points of interest about the following text or question-> "{case}"\n Do not provide a direct answer if it is a question but only the points of interest about the question'''
    )  
    highlight_poi_chain = prompt | r
    print("Invoking in highlight_poi...")
    pois = highlight_poi_chain.invoke({"case": case})
    print("Points of Interest:\n " + pois)
    return pois

#function that takes the points of interest and places them in a list
def poi_to_list(poi, r): 
    prompt = PromptTemplate(
        input_variables = ["poi"],
        template = '''Place all the points of interest in the following text in a python list
        with this format-> ["point_of_interest: extra_information"] and let that be your only response: {poi}'''
    )  
    prompt2 = PromptTemplate(
        input_variables = ["poi_unrefined"],
        template = '''Return only the python list in the following text with no preamble: {poi_unrefined}'''
    ) 
    poi_list_unrefined_chain = prompt | r | StrOutputParser()
    poi_list_refined_chain = prompt2 | r
    poi_list_chain = poi_list_unrefined_chain | poi_list_refined_chain
    print("Invoking in poi_to_list...")
    poi_list = poi_list_chain.invoke({"poi": poi})
    print("Points of Interest List:\n " + poi_list)
    return poi_list

#function that gets more information on each PoI (optional)
def research_poi(poi_list, r):
    r_poi_list = []
    prompt = PromptTemplate(
        input_variables = ["poi"],
        template = '''Provide detailed information on the following text: {poi}'''
    )  
    r_poi_chain = prompt | r | StrOutputParser()
    print("Invoking in research_poi...")
    for poi in poi_list:
        print("new invoke...")
        r_poi = r_poi_chain.invoke({"poi": poi})
        r_poi_list.append(r_poi)
    print("r_poi list below: \n")
    print(r_poi_list)
    return r_poi_list

#function that determines whether the input requires an reply  
def require_reply(text, r):
    prompt = PromptTemplate(
        input_variables = ["text"],
        template = '''Does the following text require an answer?: {text}. Reply only with yes or no and your reason'''
    )  
    require_reply_chain = prompt | r
    answer = require_reply_chain.invoke({"text": text})
    print("Requires reply?: " + answer)
    return answer

#function that is used to get temperature for reply depending on the input
def advise_temperature(text, r):
    prompt = PromptTemplate(
        input_variables = ["text"],
        template = '''A reply to this text-> "{text}", needs to be generated from an LLM. 
        Give one suitable value for the LLM's temperature setting for the reply. 
        The temperature value is on a scale of 0 to 1.
        Do not give more than one value or a range of values'''
    )  
    advise_temperature_chain = prompt | r
    print("Invoking advise_temperature...")
    temp = advise_temperature_chain.invoke({"text": text})
    print("Advised temperature: " + temp)
    return temp

#function to form an ending opinion (eo) from the input and PoIs
def form_eo(the_input, poi_list, sps, r):
    if sps != '':
        prompt = PromptTemplate(
            input_variables = ["the_input", "poi_list", "sps"],
            template = '''Input: {the_input}\nPoints of Interest: {poi_list}\nImportant instructions: {sps}\nGive a reply to the input using the points of interest. Ensure you follow the important instructions when generating your reply'''
        )  
        form_eo_chain = prompt | r
        print("Invoking in form_eo...")
        eo = form_eo_chain.invoke({"the_input": the_input, "poi_list": poi_list, "sps": sps})
        print("Ending Opinion: " + eo)
        return eo 
    else:
        prompt = PromptTemplate(
            input_variables = ["the_input", "poi_list"],
            template = '''Input: {the_input}\nPoints of Interest: {poi_list}\nGive a reply to the input using the points of interest'''
        )  
        form_eo_chain = prompt | r
        print("Invoking in form_eo...")
        eo = form_eo_chain.invoke({"the_input": the_input, "poi_list": poi_list})
        print("Ending Opinion: " + eo)
        return eo   

#essentially delegated the task of ensuring it follows the instructions from the above function to the one below
#so it's either the one above (modified) is used directly or the one above (unmodifed) is used in conjuction with the one below

#may use this function instead to ensure the output follows the state_prompts (eo->determine issue->create sp for issue->modify eo according to sp)
def fit_eo_to_sps(the_input, eo, sps, r):
    prompt = PromptTemplate(
        # input_variables = ["the_input", "eo", "sps"],
        input_variables = ["eo", "sps"],

        # template = '''Input: {the_input}\nTentative output: {eo}\nInstructions: {sps}\nAbove is the tentative output to the input. Use the instructions above to modify the tentative output. Let your only response be the modified tentative output'''
        template = '''Text: {eo}\nInstructions: {sps}\nUse the instructions above to modify the modify the text. Let your ONLY response be the modified text.'''
    )  
    fit_eo_to_sps_chain = prompt | r
    print("Invoking in fit_eo_to_sps_chain...")
    # new_eo = fit_eo_to_sps_chain.invoke({"the_input": the_input, "eo": eo, "sps": sps})
    new_eo = fit_eo_to_sps_chain.invoke({"eo": eo, "sps": sps})
    print("New EO: \n" + new_eo)
    return new_eo

#function to determine whether the current PoIs are enough to provide an eo 
def is_enough_for_eo(the_input, poi_list, r):
    prompt = PromptTemplate(
        input_variables = ["the_input", "poi_list"],
        template = '''Input: {the_input}\nPoints of Interest: {poi_list}\nAre the points of interest listed above relevant enough to give a reply to the input? Answer only with "yes" or "no"'''
    )  
    is_enough_for_eo_chain = prompt | r
    print("Invoking in is_enough_for_eo...")
    is_enough = is_enough_for_eo_chain.invoke({"the_input": the_input, "poi_list": poi_list})
    print("Is Enough?: " + is_enough)
    return is_enough

#funtion to get more PoIs to form an eo. Automatically puts them in a refined list and returns the new updated poi_list
def get_more_pois(the_input, poi_list, r):
    prompt = PromptTemplate(
        input_variables = ["the_input", "poi_list"],
        template = '''Input: {the_input}\nPoints of Interest: {poi_list}\nHighlight other points of interest that are needed to give a reply to the input and that are not in the above-listed points of interest'''
    )  
    get_more_pois_chain = prompt | r
    print("Invoking in get_more_pois...")
    more_pois_unrefined = get_more_pois_chain.invoke({"the_input": the_input, "poi_list": poi_list})

    more_pois_unrefined_list_string = poi_to_list(poi = more_pois_unrefined, r = r)
    more_pois_unrefined_list = json.loads(more_pois_unrefined_list_string)
    more_pois_refined = list_to_string(the_list = more_pois_unrefined_list)
    print("The extra PoIs: \n" + more_pois_refined)

    new_pois = poi_list + "\n" + more_pois_refined
    print("\nTotal PoI list: \n" + new_pois)
    return new_pois #, more_pois_refined  

#function to determine whether there is something wrong with the tentative_eo by comparing it against the input. If there is something
#wrong, it returns the what the issue is. If there is nothing wrong, it returns no
def compare_eo_against_input(the_input, eo, r):
    prompt = PromptTemplate(
        input_variables = ["the_input", "eo"],
        template = '''Input: {the_input}\nTentative output: {eo}\nYou are to determine if the tentative output is suitable for the input. If it is not suitable, describe what the issue is. If it is suitable, let your response be that it is suitable. '''
    )  
    compare_eo_against_input_chain = prompt | r
    print("Invoking in compare_eo_against_output...")
    comparison_answer = compare_eo_against_input_chain.invoke({"the_input": the_input, "eo": eo})
    print("After comparison, is there something wrong?: " + comparison_answer)
    return comparison_answer

#funtion to determine if the tentative output follows the state_prompts
def follows_sps(eo, sps, r):
    prompt = PromptTemplate(
        input_variables = ["the_input", "eo"],
        # template = '''Tentative output: {eo}\nInstructions: {sps}\nYou are to determine if the tentative output follows all the above-listed instructions. If it does not, describe what the issue is. If it follows all, let your response be "Affirmative". '''
        template = '''{eo}\nYou are to determine if the text above follows all these instructions: {sps}\nIf it does not, describe what the issue is. If it follows all, let your response be "Affirmative". '''
    )  
    follows_sps_chain = prompt | r
    print("Invoking in follows_sps_chain...")
    follows_sps_answer = follows_sps_chain.invoke({"eo": eo, "sps": sps})
    print("Follows all state_prompts: " + follows_sps_answer)
    return follows_sps_answer

#function to get a new state_prompt to solve an issue detected in the tentative_eo after comparison against the input
def get_new_sp_for_eo(the_input, eo, issue, r):
    prompt = PromptTemplate(
        input_variables = ["the_input", "eo", "issue"],
        template = '''Input: {the_input}\nTentative output: {eo}\nIssue detected: {issue}\nAbove is an issue detected with the tentative output for the above input. Write a suitable instruction prompt to solve the issue'''
    )  
    get_new_sp_for_eo_chain = prompt | r
    print("Invoking in get_new_sp_for_eo_chain...")
    new_sp = get_new_sp_for_eo_chain.invoke({"the_input": the_input, "eo": eo, "issue": issue})
    print(f"\nIssue: {issue}\nNew state_prompt: {new_sp}")
    return new_sp

#function to get the exact issue gotten from compare_eo_against_input
def get_issue_exactly(text, r):
    prompt = PromptTemplate(
        input_variables = ["text"],
        template = '''Text: {text}.\nLet your ONLY response be the issue that is mentioned in the text above'''
    )  
    get_issue_exactly_chain = prompt | r | StrOutputParser()
    exact_issue = get_issue_exactly_chain.invoke({"text": text})
    print("\nExact issue: " + exact_issue + "\n")
    return exact_issue    

#function to get the exact state_prompt gotten from get_new_sp_for_eo
def get_sp_exactly(text, r):
    prompt = PromptTemplate(
        input_variables = ["text"],
        template = '''Text: {text}.\nLet your ONLY response be the instruction that is conveyed in the text above.'''
    )  
    get_sp_exactly_chain = prompt | r | StrOutputParser()
    exact_sp = get_sp_exactly_chain.invoke({"text": text})
    print("\nExact State Prompt: " + exact_sp + "\n")
    return exact_sp 

#funtion to get instructions given in the output if any
def get_sp_from_input(case, r):
    prompt = PromptTemplate(
        input_variables = ["case"],
        template = '''Text: {case}\nGo through the above text and let your response be any instructions that are given in it (give your reason too). If there are no instructions, let your ONLY response be "Instructionless"'''
    )  
    get_sp_from_input_chain = prompt | r
    print("Invoking in get_sp_from_input_chain...")
    sp_from_input = get_sp_from_input_chain.invoke({"case": case})

    no_instruction_match = re.match(r'^(Instructionless|instructionless)', sp_from_input.strip())
    if no_instruction_match: #no instructions found
        return False
    else:
        print(f"Raw sp_from_input: {sp_from_input}")
        sp_from_input = get_sp_exactly(text = sp_from_input, r = r)
        print(f"\nFound state_prompt in input: {sp_from_input}\n")
        return sp_from_input




#Below are the utility functions

#funtion to return only the number in a particular text
def get_number_only(text, r):
    prompt = PromptTemplate(
        input_variables = ["text"],
        template = '''Return only the number this text is conveying with no additional
        text or information: {text}. Let the number be your only response'''
    )  
    number_only_chain = prompt | r
    number_only = number_only_chain.invoke({"text": text})
    print(f"{text} ---> get_no_only: " + number_only)
    return float(number_only)

#function to determine whether compare_eo_against_input is saying yes or no
def determine_yes_or_no(text, r):
    #You are to determine whether the above text is conveying a "No" or "Yes"
    prompt = PromptTemplate(
        input_variables = ["text"],
        template = '''Text: {text}.\nIs the text above conveying that the tentative output is suitable?. If it is conveying that it's suitable, let your only response be "Sufficient". If it is conveying that it is not suitable, let your only response be "Unsuitable".'''
    )  
    determine_yes_or_no_chain = prompt | r
    determined_answer = determine_yes_or_no_chain.invoke({"text": text})
    print(f"({text}) ---> get_ans only: " + determined_answer)
    return determined_answer

#function to deterine if follows_sps is returning affirmative or not
def is_not_affirmative(text, r):
    prompt = PromptTemplate(
        input_variables = ["text"],
        template = '''Text: {text}.\nYou are to determine whether the above text conveying "Affirmative". If it is conveying "Affirmative" let your response be "No". If it is NOT conveying "Affirmative" let your only response be "Yes".'''
    )  
    is_not_affirmative_chain = prompt | r
    determined_answer = is_not_affirmative_chain.invoke({"text": text})
    print(f"({text}) ---> saying is not affirmative?: " + determined_answer)
    return determined_answer

#funtion that converts the python list of PoIs to a refined list
def list_to_string(the_list):
    the_string = ''
    for item in the_list:
        item = item + '\n'
        the_string += item
    print("the_string: \n" + the_string)
    return the_string