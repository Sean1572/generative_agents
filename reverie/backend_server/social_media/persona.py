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
from persona.cognitive_modules.reflect import generate_focal_points, generate_insights_and_evidence

def get_history_of_other_persona(user, post, personas):
    print(personas, post)
    op = personas[post["persona"]]

    # BASED ON agent_chat_v2 in converse.py
    focal_points = [f"{op.scratch.name}"]
    retrieved = new_retrieve(user, focal_points, 5)
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
        retrieved = new_retrieve(user, focal_points, 5)
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
    retrieved = new_retrieve(user, focal_points_main, 1)
    return retrieved, social_media_message

def does_genearte_post(persona, post=None):
    ## TODO CREATE A SYSTEM TO DECIDE IF THE USER WANTS TO POST SOMETHING
    pass

def post_interact(post, persona, personas):
    # BASED ON agent_chat_v2 in converse.py
    retrieved, social_media_message = get_history_of_other_persona(persona, post, personas)

    print(len(social_media_message))
    #input()

    output, _ = run_gpt_generate_comment(persona, personas[post["persona"]], retrieved, social_media_message)
    
    print ("COMMENT", output)
    #input()

    ## TODO FORMAT AS A CONVERSATION
    return output,0, social_media_message

def generate_post(persona):
    focal_points = generate_focal_points(persona, 3)
    # Retrieve the relevant Nodes object for each of the focal points. 
    # <retrieved> has keys of focal points, and values of the associated Nodes. 
    retrieved = new_retrieve(persona, focal_points)
    
    ## Get some facts about the persona's life and thoughts
    statements = []
    insights = []
    for focal_pt, nodes  in retrieved.items(): 
        for v in nodes: 
            statements.append(f"- {v.description})")
        
        insights.append(str(generate_insights_and_evidence(persona, nodes, n=5)))

    print("===============PRE GENERATE POST===============")
    print(statements)
    print(insights)
    generated_post, test = run_gpt_generate_post(persona, statements, insights)
    print(test)
    print(generated_post)
    print("===============ENDGENERATE POST===============")
    return generated_post, 0


def _react_to_other_post(post_interaction, duration_min_temp, post, persona):
    _process_social_media_thoughts(persona, 
        f"""
        {persona.scratch.name} saw the following social media thread:

        THREAD START
        {post}
        THREAD END

        and in response {persona.scratch.name} added the following comment:

        COMMENT START
        {post_interaction}
        COMMENT END
        """
    )

def _react_to_our_post(post, duration_min_temp, persona):
    _process_social_media_thoughts(persona, 
        f"{persona.scratch.name} made a post on social media and wrote the following: \n {post}"
    )

def _process_social_media_thoughts(persona, context):
    thought = context
    created = persona.scratch.curr_time
    expiration = persona.scratch.curr_time + datetime.timedelta(days=5)
    s, p, o = (persona.scratch.name, "interacted", "social media")
    keywords = set(["social media", "post", "online"])

    print(len(context))
    #input()

    thought_poignancy = generate_poig_score(persona, "event", context)
    thought_embedding_pair = (thought, get_embedding(thought))
    persona.a_mem.add_thought(created, expiration, s, p, o, 
                                thought, keywords, thought_poignancy, 
                                thought_embedding_pair, None)

def spend_time_on_social_media(persona, media, time, personas, top_k=5):
    ## Get current state of social media posts (top x)
    last_5_posts = media.get_content()

    ## GENERATE A USER'S INTERACTION WITH SOCIAL MEDIA
    duration_min = 0
    post_interactions = []
    print("HERE", last_5_posts)
    #input()

    for id, post in last_5_posts:
        social_media_message = ""
        if True: #if does_generate_post(persona, post): #TODO CREATE A DECSION SYSTEM
            post_interaction, duration_min_temp, social_media_message = post_interact(post, persona, personas)
            post_interactions.append(post_interaction)
            
            media.write_comment(persona.scratch.name, id, post_interaction, str(persona.scratch.curr_time))
            media.save()
            _react_to_other_post(post_interaction, duration_min_temp, social_media_message, persona)

    if True: #if does_generate_post(persona, None): #TODO CREATE A DECSION SYSTEM
        post, duration_min_temp = generate_post(persona)
        duration_min += duration_min_temp
        media.write_post(persona.scratch.name, post, str(persona.scratch.curr_time))
        media.save()
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