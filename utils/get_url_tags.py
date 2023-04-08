import os 
import json 
import numpy as np

tags = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','dataset/model/', 'tags.json'))
def get_url(arxiv_id):
    # Get url from arxiv_id
    # Id should be in YYMM.NNNNN format but sometimes it's not
    # so we have to add a leading 0 if necessary
    arxiv_id = str(arxiv_id)
    try:
        first_part = arxiv_id.split(".")[0]
        second_part = arxiv_id.split(".")[1]
    except:
        # Weird ids like quant-ph/0207118
        return "https://arxiv.org/abs/" + arxiv_id

    if len(first_part) != 4:
        while len(first_part) < 4:
            first_part = "0" + first_part

    if len(second_part) != 5:
        while len(second_part) < 5:
            second_part = "0" + second_part

    return "https://arxiv.org/abs/" + first_part + "." + second_part

def load_user_tags():
    print("Loading user tags!")
    with open(tags, "r") as f:
        user_tags = json.load(f)

    return user_tags

def get_user_tags_from_query(query, user_tag_keys, model):
    # This will embedd the query and then compare it to the user tags (key + values)

    # Get the embeddings of the query
    query_embedding = model.encode(query, convert_to_tensor=True).cpu()

    # Get the embeddings of the user tags
    to_encode = [f"{key} - {','.join(value)}" for key, value in load_user_tags().items() if key in user_tag_keys]
    user_tags_embeddings = model.encode(to_encode, convert_to_tensor=True).cpu()

    # Compute the dot product
    dot_product = np.dot(query_embedding, user_tags_embeddings.T)

    # Get the tags and probabilities
    return [(tag, prob) for tag, prob in zip(user_tag_keys, dot_product)]