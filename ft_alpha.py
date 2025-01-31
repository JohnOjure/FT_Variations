from ft_alpha_factors import *
from langchain_ollama import OllamaLLM
import json
import re

#the ft_alpha variation
#- Only produces EOs
#- Takes no actions
#- In a particular run, the state_prompts are used and are not classified or grouped
#- No origination capability

#sample cases
#- Why are bumblebees' abdomens big? Answer in only 10 words with no punctuation.
#- 

llm = OllamaLLM(model = 'llama3', temperature = 0.1)

#state_prompts
state_prompts = ""

#the input case
text_in_use = input("Case: ")

#get any state_prompts from the input case and add them to the state_prompts list
sp_from_case = get_sp_from_input(case = text_in_use, r = llm)
if sp_from_case == False:
    print("No instructions in state_prompt")
else:
    state_prompts = state_prompts + "\n" + f"->{sp_from_case}"
    print("\nState_Prompts: \n" + state_prompts + "\n")

#obtaining points of interest from the input
points_of_interest = highlight_poi(case = text_in_use, r = llm)
points_of_interest_list_string = poi_to_list(poi = points_of_interest, r = llm)
points_of_interest_list = json.loads(points_of_interest_list_string)
poi_list_refined = list_to_string(the_list = points_of_interest_list)

#determine if the input requires a reply (won't use this in this variation)
y_n = require_reply(text = text_in_use, r = llm)

#getting the temperature to use
temp_str = advise_temperature(text = text_in_use, r = llm)
temp_num = get_number_only(text = temp_str, r = llm)

#N1 wrapped is for ensuring the pois are sufficient to generate a reply
#N1 wrapped
not_enough = True
original_temp = llm.temperature
print("Original temperature: " + str(original_temp))

while not_enough:
    print("Start of the not_stop while loop")
    llm.temperature = temp_num
    print("New temperature: " + str(llm.temperature))
    is_enough = is_enough_for_eo(the_input = text_in_use, poi_list = poi_list_refined, r = llm)
    is_enough_match = re.match(r'^(Yes|yes)', is_enough.strip())

    if is_enough_match:
        ending_opinion = form_eo(the_input = text_in_use, poi_list = poi_list_refined, sps = state_prompts, r = llm)
        llm.temperature = original_temp
        print("Temperature restored to original: " + str(llm.temperature))
        print("\n")
        not_enough = False
    else:
        poi_list_refined = get_more_pois(the_input = text_in_use, poi_list = poi_list_refined, r = llm)
#N1 wrapped end

#N2 wrapped is to check whether the answer has an issue when compared against the input
#N2 wrapped
still_an_issue = True
ending_opinion_n2 = ending_opinion

while still_an_issue:
    print("start of while still_an_issue loop")
    issue_or_not = compare_eo_against_input(the_input = text_in_use, eo = ending_opinion_n2, r = llm) #determine if there is an issue when compared against the input
    issue_polarity = determine_yes_or_no(text = issue_or_not, r = llm) #get the exact answer of the returned answer above
    issue_or_not_match = re.match(r'^(Sufficient|sufficient)', issue_polarity.strip()) #re string matching

    if not issue_or_not_match: #if there is an issue
        exact_issue = get_issue_exactly(text = issue_or_not, r = llm)

    else: #if there is apparently no issue, check again using follows_sps factor
        follows_all_sps = follows_sps(eo = ending_opinion_n2, sps = state_prompts, r = llm)
        is_not_affirmative_answer = is_not_affirmative(text = follows_all_sps, r = llm)
        follows_all_match = re.match(r'^(No|no)', is_not_affirmative_answer.strip())
        # print("Follows_match: " + follows_all_match)

        if follows_all_match: #if it follows all state_prompts
            print("Follows all state_prompts!")
            exact_issue = "None at all"
        else: #if it does not follow all state_prompts
            print("Doesn't follow all state_prompts!")
            exact_issue_about_following_sps = get_issue_exactly(text = follows_all_sps, r = llm)

            #get a state prompt to solve the issue
            sp_for_follow = get_new_sp_for_eo(the_input = text_in_use, eo = ending_opinion_n2, issue = exact_issue_about_following_sps, r = llm)
            sp_for_follow = get_sp_exactly(text = sp_for_follow, r = llm)

            #add the state_prompt to the list of state_prompts so that it won't make the same issue in future EOs
            state_prompts = state_prompts + "\n" + f"->{sp_for_follow}"
            print("\nState_Prompts: \n" + state_prompts + "\n")

            #then fit it to the current state prompts (correct the issue and any potential others)
            ending_opinion_n2 = fit_eo_to_sps(the_input = text_in_use, eo = ending_opinion_n2, sps = state_prompts, r = llm)
            continue

    if not issue_or_not_match: #if there is an issue
        print("Issue detected!")

        #get a state prompt to solve the issue
        sp = get_new_sp_for_eo(the_input = text_in_use, eo = ending_opinion_n2, issue = exact_issue, r = llm)
        sp = get_sp_exactly(text = sp, r = llm)

        #add the state_prompt to the list of state_prompts so that it won't make the same issue in future EOs
        state_prompts = state_prompts + "\n" + f"->{sp}"
        print("\nState_Prompts: \n" + state_prompts + "\n")

        #then fit it to the current state prompts (correct the issue and any potential others)
        ending_opinion_n2 = fit_eo_to_sps(the_input = text_in_use, eo = ending_opinion_n2, sps = state_prompts, r = llm)
    else: #not an issue
        print("\n")
        print("Final Ending Opinion: \n" + ending_opinion_n2)
        print("\n")
        still_an_issue = False
#N2 wrapped end

print("State_prompts: " + state_prompts)
print("End")
