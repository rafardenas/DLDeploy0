import config
import torch

import flask
from flask import Flask
from flask import request
from model import BERTBaseUncased
import transformers

import os
import sys

sys.path.append(os.getcwd())

app = Flask(__name__)

MODEL = None
DEVICE = "cpu"

def sentence_prediction(sentence):
    tokenizer = config.TOKENIZER
    max_len = config.MAX_LEN
    review = str(sentence)
    
    inputs = tokenizer.encode_plus(
    review, 
    None, 
    add_special_tokens=True,
    max_length=max_len,
    #pad_to_max_length=True
    padding='max_length',
    truncation=True
    )

    ids = inputs["input_ids"]
    mask = inputs["attention_mask"]
    token_type_ids = inputs["token_type_ids"]

    ids = torch.tensor(ids, dtype=torch.long).unsqueeze(0)
    mask =  torch.tensor(mask, dtype=torch.long).unsqueeze(0)
    token_type_ids = torch.tensor(token_type_ids, dtype=torch.long).unsqueeze(0)
    print("shape with unsqueeze:", token_type_ids.shape)


    ids = ids.to(DEVICE,dtype=torch.long)
    mask = mask.to(DEVICE,dtype=torch.long)
    token_type_ids = token_type_ids.to(DEVICE,dtype=torch.long)

    outputs = MODEL(
        ids=ids, 
        mask=mask, 
        token_type_ids=token_type_ids
    )

    outputs = torch.sigmoid(outputs).cpu().detach().numpy()
    return outputs[0][0]


#create an endpoint
@app.route("/predict")
def predict():
    sentence = request.args.get("sentence")
    #sanity check
    inference = sentence_prediction(sentence)
    print(inference)
    response = {}
    response["response"] = {
        "Query"    : sentence,
        "positive" : str(inference),
        "negative" : str(1 - inference)
    }
    return flask.jsonify(response)

if __name__ == "__main__":
    MODEL = BERTBaseUncased()
    MODEL.load_state_dict(torch.load(config.MODEL_PATH))  #loading the trained model
    MODEL.to(DEVICE)
    MODEL.eval()
    app.run()
