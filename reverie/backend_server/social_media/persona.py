import math
import sys
import datetime
import random
sys.path.append('../')

from global_methods import *

from social_media.prompt_inputs import *

from persona.memory_structures.spatial_memory import *
from persona.memory_structures.associative_memory import *
from persona.memory_structures.scratch import *
from persona.cognitive_modules.retrieve import *
from persona.prompt_template.run_gpt_prompt import *
from persona.cognitive_modules.converse import *

def get_history_of_other_persona(user, post, personas):
    op = personas[post["persona"]]

    # BASED ON agent_chat_v2 in converse.py
    focal_points = [f"{op.scratch.name}"]
    retrieved = new_retrieve(user, focal_points, 50)
    relationship = generate_summarize_agent_relationship(user, op, retrieved)

    social_media_message = f"""
        {op.scratch.name} made a post online to social media. They said:
        -----
        {post["content"]}
        ------
        """
    
    focal_points_main = [f"{relationship}", 
                    f"{user.scratch.name} is {op.scratch.act_description}", 
                    social_media_message]

    for comments in post["comments"]:
        op_commenter = personas[comments["persona"]]
        focal_points = [f"{op_commenter.scratch.name}"]
        retrieved = new_retrieve(user, focal_points, 50)
        relationship = generate_summarize_agent_relationship(user, op_commenter, retrieved)

        social_media_message += f"""
            {op_commenter.scratch.name} commented on {op.scratch.name}'s post saying 
            -----
            {comments["content"]}
            ------
            """
        focal_points_main+=[f"{relationship}", 
                    f"{user.scratch.name} is {op_commenter.scratch.act_description}", 
                    social_media_message]
    
    # TODO: ADD LIKES
    retrieved = new_retrieve(user, focal_points_main, 30)
    return retrieved, social_media_message

def does_genearte_post(persona, post=None):
    ## TODO CREATE A SYSTEM TO DECIDE IF THE USER WANTS TO POST SOMETHING
    pass

def post_interact(post, persona, personas):
    # BASED ON agent_chat_v2 in converse.py
    retrieved, social_media_message = get_history_of_other_persona(persona, post, personas)


    curr_context = (f"{persona.scratch.name} is on social media " +
                    f" and saw a post written by {personas[post["persona"]].scratch.name} \n"
    )

    if len(post["comments"]) > 0:
        curr_context += "There are comments responding to the post written by ["
        for comments in post["comments"]:
            curr_context += f"{personas[comments["persona"]].scratch.name}",
        curr_context += "] \n"

    if len(post["likes"]) > 0:
        curr_context += "The post was liked by ["
        for pesrona in post["likes"]:
            curr_context += f"{personas[pesrona].scratch.name}",
        curr_context += "]"

    x = run_gpt_generate_comment(persona, personas[post["persona"]], retrieved, curr_context, social_media_message)
    x["utterance"], x["end"]
    print ("adshfoa;khdf;fajslkfjald;sdfa HERE", x)
    input()

    ## TODO FORMAT AS A CONVERSATION
    return x["utterance"], x["end"]

def _react_to_other_post(post_interaction, duration_min_temp, post, persona):
    pass ## TODO IMPLEMENT REACTIONS

def generate_post(persona):
    # TODO Generate a post based on how the user may generate thoughts???
    pass

def _react_to_our_post(post, duration_min_temp, persona):
    pass ## TODO IMPLEMENT REACTIONS

def spend_time_on_social_media(persona, media, time, personas, top_k=5):
    ## Get current state of social media posts (top x)
    last_5_posts = media.get_content()

    ## GENERATE A USER'S INTERACTION WITH SOCIAL MEDIA
    duration_min = 0
    post_interactions = []
    for post in last_5_posts:
        if True: #if does_generate_post(persona, post): #TODO CREATE A DECSION SYSTEM
            post_interaction, duration_min_temp = post_interact(post, persona, personas)
            post_interactions.append(post_interaction)
            duration_min += duration_min_temp
            
            ## TODO CREATE A SUMMARY?
            # Question: Should we react to every post?
            _react_to_other_post(post_interaction, duration_min_temp, post, persona)

    if True: #if does_generate_post(persona, None): #TODO CREATE A DECSION SYSTEM
        post, duration_min_temp = generate_post(persona)
        duration_min += duration_min_temp
        _react_to_our_post(post, duration_min_temp, persona)
    
    ## THIS SHOULD BE EVERYTHING THAT IS NEEDED
    
    ## NOTES
    
    ## PREP FORMATTING TO SAVE ACTIONS INTO PERSONA'S MEMORY
    # act_start_time = persona.scratch.act_start_time
    # curr_time = persona.scratch.curr_time
    # if curr_time.second != 0: 
    #     temp_curr_time = curr_time + datetime.timedelta(seconds=60 - curr_time.second)
    #     chatting_end_time = temp_curr_time + datetime.timedelta(minutes=inserted_act_dur)
    # else: 
    #     chatting_end_time = curr_time + datetime.timedelta(minutes=inserted_act_dur)
    
    ## FOR EACH POST
    ## System to decide what to do with post
    ## - Based on history of the user
    ## - Based on what they posted
    ## - Based on user
    ## - Based on relationship with them
    ## Run actions
    ## - Like posts
    ## - write comment
    ##      - generate message to write, target users
    ## - make a post
    ## OUT OF LOOP
    ## Update memory with summary of actions taken
    pass 