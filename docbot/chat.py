import random
import json
import torch
import numpy as np
from docbot.model1 import NeuralNet
from docbot.nltk_utils import bag_of_words, tokenize
from backend import settings
import os

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

base_dir = settings.BASE_DIR
cache_file_path = os.path.join(base_dir, 'docbot', 'intents.json')

with open(cache_file_path, 'r') as f:
    intents = json.load(f)

# FILE = "data.pth"
FILE = os.path.join(base_dir, 'docbot', 'data.pth')
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"


def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                botvalue = random.choice(intent['responses'])
                return botvalue

                   
    botvalue = f"I do not understand..."
    return botvalue
