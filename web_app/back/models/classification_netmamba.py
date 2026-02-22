import os, sys
import numpy as np
# ensure project root is on sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import Dict, Any, List

from scapy.all import *
import torch 
import pickle
from scipy.special import softmax
from PIL import Image
from torchvision import transforms,datasets

from data.github_repo.NetMamba.src import models_net_mamba

sys.modules['models_net_mamba'] = models_net_mamba 


device ="cuda" if torch.cuda.is_available() else "cpu"

label_mappings_netmamba=['audio', 'bittorrent', 'browsing', 'cameras', 'chat', 'cridex', 'facetime', 
'file-transfer', 'flood', 'ftp', 'geodo', 'gmail', 'home automation', 'htbot', 'hydra', 'mail', 'miuref', 
'mysql', 'neris', 'nmap', 'nsis-ay', 'outlook', 'p2p', 'shifu', 'skype', 'streaming', 'tinba', 'video',
'virut', 'voip', 'weibo', 'worldofwarcraft', 'zeus']

label_mappings_netmamba_four = {
    "CICIoT2022": ["Audio", "Cameras", "Flood", "Home-Automation", "Hydra", "Nmap"],
    "ISCXTor2016": ["Audio", "Browsing", "Chat", "File-transfer", "Mail", "P2P", "Video", "Voip"],
    "ISCXVPN2016": ["Browsing", "Chat", "Email", "Ftp", "P2P", "Streaming", "Voip"],
    "USTC_TFC2016": [
        'BitTorrent', 'Cridex', 'Facetime', 'FTP', 'Geodo', 'Gmail', 'Htbot',
        'Miuref', 'MySQL', 'Neris', 'Nsis-ay', 'Outlook', 'Shifu', 'Skype',
        'Tinba', 'Virut', 'Weibo', 'WorldOfWarcraft', 'Zeus',"test"
    ]
}

NETMAMBA_CKPTS = {
    "CICIoT2022": "./data/finetuned_NetMamba_weight_only/finetuned_NetMamba_CICIoT2022.pth",
    "ISCXTor2016": "./data/finetuned_NetMamba_weight_only/finetuned_NetMamba_ISCXTor2016.pth",
    "ISCXVPN2016": "./data/finetuned_NetMamba_weight_only/finetuned_NetMamba_ISCXVPN2016.pth",
    "USTC_TFC2016": "./data/finetuned_NetMamba_weight_only/finetuned_NetMamba_USTC-TFC2016.pth",
}

def build_dataset(folder_images):
    mean = [0.5]
    std = [0.5]

    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    #root = os.path.join(args.data_path, 'train' if is_train else 'test')
    dataset = datasets.ImageFolder(folder_images, transform=transform)

    print(dataset)

    return dataset

def netMamba_classification2(folder="./data/temp/netmamba_dataset/"):
    merge_model = models_net_mamba.__dict__["net_mamba_classifier"](
        num_classes=len(label_mappings_netmamba),
        drop_path_rate=0.1,
        byte_length=1600,
    )
    os.makedirs("./data/temp/netmamba_dataset/dummy_class",exist_ok=True)
    merge_model=merge_model.to(device)
    check_point=torch.load("./data/finetuned_merge_models/finetuned_netmamba_merge_model_small.pth",map_location=device)
   
    err,unp=merge_model.load_state_dict(check_point["model"],strict=False)
    print(err)
    print(unp)
    #print(merge_model)
    merge_model.eval()
    merge_model.to(device)
    #Transform the image
    images=build_dataset(folder)
    dataloader=torch.utils.data.DataLoader(
        images,
        batch_size=4
    )
    #output=merge_model(image)
    #print(output)
    for batch in dataloader:
        print("here in the merge  model for netmamba")
        image=batch[0]
        image=image.to(device,non_blocking=True)
        with torch.inference_mode():
            logits=torch.flatten(merge_model(image)).tolist()
            probabilities = softmax(logits)
            print(probabilities)
            dataset_predictions = dict(zip(label_mappings_netmamba, probabilities))
            print(dataset_predictions)  
        
        
    return dataset_predictions


def netMamba_classification(folder="./data/temp/netmamba_dataset/"):
    all_predictions = {}

    images = build_dataset(folder)
    dataloader = torch.utils.data.DataLoader(images, batch_size=4)

    for dataset_name, ckpt_path in NETMAMBA_CKPTS.items():
        print(f"\nRunning NetMamba on {dataset_name}")

        labels = label_mappings_netmamba_four[dataset_name]

        model = models_net_mamba.__dict__["net_mamba_classifier"](
            num_classes=len(labels),
            drop_path_rate=0.1,
            byte_length=1600,
        ).to(device)

        checkpoint = torch.load(ckpt_path, map_location=device)
        err, unp = model.load_state_dict(checkpoint, strict=False)
        print("Missing keys:", err)
        print("Unexpected keys:", unp)

        model.eval()

        dataset_probs = []

        with torch.inference_mode():
            for batch in dataloader:
                image = batch[0].to(device, non_blocking=True)

                logits = model(image)
                logits = torch.flatten(logits).tolist()
                probabilities = softmax(logits)

                preds = dict(zip(labels, probabilities))
                dataset_probs.append(preds)

        all_predictions[dataset_name] = dataset_probs

        best_preds = []
        for dataset_name, preds_list in all_predictions.items():
            sorted_preds = sorted(
                preds_list[0].items(), key=lambda x: x[1], reverse=True
            )
            best_preds.append(sorted_preds[0])
        best_predictions=dict(best_preds)

            
    print(best_predictions)
    return best_predictions



def process_netmamba_logits(netmamba_output: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
    """
    Process NetMamba logits for all datasets.
    
    Args:
        netmamba_output: {
            "netmamba_ustc_tfc": [logit1, logit2, ...],
            "netmamba_ciciot": [...],
            ...
        }
    
    Returns:
        Dictionary mapping dataset names to class probabilities
    """
    dataset_predictions = {}
    
    for key, logits in netmamba_output.items():
        dataset_mapping = {
            "netmamba_ustc_tfc": "USTC_TFC2016",
            "netmamba_ciciot": "CICIOT",
            "netmamba_iscx_vpn": "ISCX_VPN2016",
            "netmamba_iscx_tor": "ISCX_TOR2016"
        }
        
        dataset_name = dataset_mapping.get(key)
        if dataset_name:
            probabilities = softmax(logits)
            class_names = label_mappings_netmamba.get(dataset_name, [])
            class_probs = dict(zip(class_names, probabilities))
            
            dataset_predictions[dataset_name] = class_probs
    
    return dataset_predictions

if __name__=="__main__":
    print(device)
    print(len(label_mappings_netmamba))
    netMamba_classification()
