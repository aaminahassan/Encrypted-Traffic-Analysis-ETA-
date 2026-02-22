import sys
import os
import torch
import argparse
from scipy.special import softmax
import collections
import torch.nn as nn
from typing import Dict, Any, List

#adding etBert module path 
actual_dir=os.path.dirname(os.path.abspath(__file__))
parent_dir=os.path.dirname(actual_dir)
etBert_dir=os.path.join(parent_dir,"data/github_repo/EtBert")
uer_dir=os.path.join(parent_dir,"data/github_repo/EtBert/uer/")
import yaml
#sys.path.insert(0, uer_dir)

# Add the parent directory to sys.path
if etBert_dir not in sys.path:
    sys.path.insert(0, etBert_dir)

from uer.utils.constants import *
from uer.utils import *
from uer.utils.config import load_hyperparam
from uer.utils.seed import set_seed
from uer.model_loader import load_model
from uer.opts import infer_opts
from uer.layers import *
from fine_tuning.run_classifier_kaggle import Classifier

label_mappings_etbert = ['Audio', 'BitTorrent', 'Browsing', 'Cameras', 'Chat', 'Cridex','Email',
       'FTP', 'Facetime', 'File-Transfer', 'Flood', 'Ftp', 'Geodo',
       'Gmail', 'Home-Automation', 'Htbot', 'Hydra', 'Mail', 'Miuref',
       'MySQL', 'Neris', 'Nmap', 'Nsis-ay', 'Outlook', 'P2P', 'SMB',
       'Shifu', 'Skype', 'Streaming', 'Tinba', 'Video', 'Virus', 'Voip',
       'Weibo', 'WorldOfWarcraft', 'zeus']

def init_model(labels_num,finetuned_model_path):
    with open("./data/etbert_config.yml","r") as f:
        default_args=yaml.load(f,Loader=yaml.SafeLoader)
    
    # Convert dict to argparse.Namespace
    args = argparse.Namespace(**default_args)
    args.labels_num=labels_num
    args.finetuned_model_path=finetuned_model_path
    # Then continue your pipeline
    #args = load_hyperparam(args)
    args.tokenizer = str2tokenizer[args.tokenizer](args)
    args.soft_targets, args.soft_alpha = False, False
    args.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    model = Classifier(args)
    model.load_state_dict(torch.load(args.finetuned_model_path, map_location=args.device))
    
    model = model.to(args.device)
    print("Model initialized.")
    return args,model

#initiate the models 
args,etbert_merge=init_model(len(label_mappings_etbert),"./data/finetuned_merge_models/finetuned_etbert_model_merge.bin")
packet=''

def etbert_inference(packet):
    #print(packet[0])
    #turn into embedding and get also the seg even if u have only on 
    src = args.tokenizer.convert_tokens_to_ids([CLS_TOKEN] + args.tokenizer.tokenize(packet[0])) #list id
    #print(src)
    torch.tensor(src)
    seg = [1] * len(src) # list of 1
    if len(src) > args.seq_length:
        src = src[: args.seq_length]
        seg = seg[: args.seq_length]
    while len(src) < args.seq_length:
        src.append(0)
        seg.append(0)
    src=torch.LongTensor([src])
    seg=torch.LongTensor([seg])
    src=src.to(args.device)
    seg=seg.to(args.device)


    logits=torch.flatten(etbert_merge(src,tgt=None,seg=seg)[1]).tolist()
    probabilities = softmax(logits)
    dataset_predictions = dict(zip(label_mappings_etbert, probabilities))

    return dataset_predictions  


if __name__=='__main__':

    print(len(label_mappings_etbert))
    args,etbert_merge=init_model(len(label_mappings_etbert),"./data/finetuned_merge_models/finetuned_etbert_model_merge.bin")
    packet=["c1d8 d805 0562 62b9 b95b 5b10 10d4 d46d 6db5 b51e 1e66 6655 553d 3d7d 7dd9 d9a6 a6bb bbdd ddbf bf1c 1ce3 e36e 6e86 86ea eace ce65 65a0 a0a5 a527 274b 4bd3 d376 7612 1204 047b 7bcf cf77 77cc cc96 964b 4bdc dc7f 7fd8 d866 666e 6e76 7622 22d1 d1a4 a477 7717 171c 1cf3 f3a6 a68f 8fa4 a4df dfd3 d3f4 f494 948b 8b5c 5c57 577e"]
    packet2=["1069 690f 0f49 4909 0904 049e 9e1c 1c4a 4a57 5750 5010 1001 01f3 f3fe fe0a 0a00 0000 0047 4781 8181 810e 0eeb ebc1 c16e 6ef2 f2dc dc76 76cb cba6 a618 188e 8e66 66f4 f45d 5d7c 7c4f 4f7d 7dab abe1 e118 1846 4659 59e0 e089 894b 4b37 3758 5877 7704 04b3 b3de de34 3427 27da da61 6121 2182 8235 35a0 a0de de58 58a8 a8de de65"]
    proba= etbert_inference(packet)
    print(proba)
   

