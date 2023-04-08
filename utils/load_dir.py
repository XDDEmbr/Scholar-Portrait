import os
from os.path import join,  exists

current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
data_dir = join(parent_dir, "dataset")
model_dir = join(data_dir, "model")
testing = True

for dir in [data_dir, model_dir]:
    if not exists(dir):
        os.mkdir(dir)