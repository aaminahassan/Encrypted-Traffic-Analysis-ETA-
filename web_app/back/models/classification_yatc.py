import json
import os
import sys
import torch
from scipy.special import softmax
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, SequentialSampler
from fastapi import UploadFile, APIRouter
from io import BytesIO
from scapy.all import rdpcap
from typing import Dict, Any, List


# ------------------------------
# PATH SETUP
# ------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
back_dir = os.path.dirname(script_dir)
if back_dir not in sys.path:
    sys.path.insert(0, back_dir)

from data.github_repo.yatc_model import models_YaTC

device = "cuda" if torch.cuda.is_available() else "cpu"

# ------------------------------
# Labels
# ------------------------------
label_mappings_yatc_all =['audio', 'bittorrent', 'browsing', 'cameras', 'chat', 'cridex', 
'facetime', 'file-transfer', 'flood', 'ftp', 'geodo', 'gmail', 'home_automation', 'htbot',
'hydra', 'mail', 'miuref', 'mysql', 'neris', 'nmap', 'nsis-ay', 'outlook', 'p2p', 'shifu',
'skype', 'smb', 'streaming', 'tinba', 'video', 'virut', 'voip', 'weibo', 'worldofwarcraft', 'zeus']

YATC_CKPTS = {
    "CICIoT2022": "data/finetuned_yatc_weight_only/finetuned_yatc_CICIoT2022_MFR.pth",
    "ISCXTor2016": "data/finetuned_yatc_weight_only/finetuned_yatc_ISCXTor2016_MFR.pth",
    "ISCXVPN2016": "data/finetuned_yatc_weight_only/finetuned_yatc_ISCXVPN2016_MFR.pth",
    "USTC_TFC2016": "data/finetuned_yatc_weight_only/finetuned_yatc_USTC-TFC2016_MFR.pth",
}


label_mappings_yatc = {
    "CICIoT2022": ["Audio", "Cameras", "Flood", "Home-Automation", "Hydra", "Nmap"],
    "ISCXTor2016": ["Audio", "Browsing", "Chat", "File-transfer", "Mail", "P2P", "Video", "Voip"],
    "ISCXVPN2016": ["Chat", "Email", "Ftp", "Streaming","P2P", "Voip","Browsing"],
    "USTC_TFC2016": [
        'BitTorrent', 'Cridex', 'Facetime', 'FTP', 'Geodo', 'Gmail', 'Htbot',
        'Miuref', 'MySQL', 'Neris', 'Nsis-ay', 'Outlook', 'Shifu', 'Skype',"SMB",
        'Tinba', 'Virut', 'Weibo', 'WorldOfWarcraft', 'Zeus'
    ]
}



#model_path="./data/finetuned_merge_models/finetuned_yatc_merge_model.pth"
#model = models_YaTC.__dict__["TraFormer_YaTC"](num_classes=len(label_mappings_yatc), drop_path_rate=0.1)
#checkpoint_model = torch.load(model_path, map_location=device, weights_only=True)
#msg = model.load_state_dict(checkpoint_model, strict=False)
#print(f"{os.path.basename(model_path)} loaded: {msg}")
#model.to(device)
#model.eval()


# ------------------------------
# INFERENCE FUNCTION
# ------------------------------
def yatc_inference2(data_path="./data/temp/yatc_dataset", batch_size=1):
    """Run inference using preloaded YaTC models."""
   

    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5]),
    ])

    test_dataset = datasets.ImageFolder(data_path, transform=transform)
    data_loader = DataLoader(
        test_dataset,
        sampler=SequentialSampler(test_dataset),
        batch_size=batch_size,
        num_workers=1,
        pin_memory=False,
        drop_last=False,
    )

    model_path="./data/finetuned_merge_models/finetuned_yatc_merge_model.pth"
    model = models_YaTC.__dict__["TraFormer_YaTC"](num_classes=len(label_mappings_yatc_all), drop_path_rate=0.1)
    checkpoint_model = torch.load(model_path, map_location=device, weights_only=True)
    msg = model.load_state_dict(checkpoint_model, strict=False)
    print(f"{os.path.basename(model_path)} loaded: {msg}")
    model.to(device)
    model.eval()

   
    for batch in data_loader:
        # print(type(batch))
        # print(len(batch))
        # print(batch[0][0].shape)
        # print(batch[0][0])
        # print("----------------------------------------------------------------------")
        #y= torch.unsqueeze(batch[0][1], dim=0)
        #print(y.shape)
        print("here in the merge model for yatc")
        images = batch[0].to(device, non_blocking=True)
        with torch.inference_mode():
            logits = torch.flatten(model(images)).tolist()
            probabilities = softmax(logits)
            dataset_predictions = dict(zip(label_mappings_yatc_all, probabilities))
            print(dataset_predictions) # only process one batch for now
            print("----------------------------------------------------------------------")
    
    print(dataset_predictions)
    return dataset_predictions


def yatc_inference(
    data_path="./data/temp/yatc_dataset",
    batch_size=1,
):
    all_predictions = {}

    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5]),
    ])

    test_dataset = datasets.ImageFolder(data_path, transform=transform)
    data_loader = DataLoader(
        test_dataset,
        sampler=SequentialSampler(test_dataset),
        batch_size=batch_size,
        num_workers=1,
        pin_memory=False,
        drop_last=False,
    )

    for dataset_name, ckpt_path in YATC_CKPTS.items():
        print(f"\nRunning YaTC on {dataset_name}")

        class_labels = label_mappings_yatc[dataset_name]

       
        model = models_YaTC.__dict__["TraFormer_YaTC"](
                num_classes=len(class_labels),
                drop_path_rate=0.1
        ).to(device)

        checkpoint = torch.load(ckpt_path, map_location=device)
        model.load_state_dict(checkpoint, strict=True)
        model.eval()

        dataset_probs = []

        with torch.inference_mode():
            for batch in data_loader:
                images = batch[0].to(device, non_blocking=True)

                logits = model(images)               # (B, C)
                probs = torch.softmax(logits, dim=1) # (B, C)

                for p in probs:
                    preds = dict(zip(class_labels, p.cpu().tolist()))
                    dataset_probs.append(preds)

                break  # keep only first batch (remove if you want full dataset)

        all_predictions[dataset_name] = dataset_probs

    # Extract top-1 prediction per dataset (from first sample)
    best_preds = []
    for dataset_name, preds_list in all_predictions.items():
        sorted_preds = sorted(
            preds_list[0].items(),
            key=lambda x: x[1],
            reverse=True
        )
        best_preds.append(sorted_preds[0])
        best_predictions=dict(best_preds)

            
    print(best_predictions)
    return best_predictions

  

if __name__=="__main__":    
    yatc_inference2()

    

