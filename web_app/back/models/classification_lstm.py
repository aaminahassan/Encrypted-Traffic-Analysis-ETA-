#now je dois creer un dataframe ou store les sentences et words sous forme de vecteur
from tensorflow.keras.models import load_model
from scipy.special import softmax
import numpy as np

# ------------------------------
# LABELS
# ------------------------------
label_mappings_etbert = ['Audio', 'BitTorrent', 'Browsing', 'Cameras', 'Chat', 'Cridex',
       'FTP', 'Facetime', 'File-Transfer', 'Flood', 'Ftp', 'Geodo',
       'Gmail', 'Home-Automation', 'Htbot', 'Hydra', 'Mail', 'Miuref',
       'MySQL', 'Neris', 'Nmap', 'Nsis-ay', 'Outlook', 'P2P', 'SMB',
       'Shifu', 'Skype', 'Streaming', 'Tinba', 'Video', 'Virus', 'Voip',
       'Weibo', 'WorldOfWarcraft', 'zeus']

# ------------------------------
# INFERENCE
# ------------------------------

def lstm_inference(packets):
    
    lstm_merge =load_model("./data/finetuned_merge_models/lstm_plus_attention_merge.keras")

    packet={"text_input":np.array(packets)}
    
    logits=lstm_merge(packet).numpy().flatten().tolist()
    probabilities = softmax(logits)
    dataset_predictions = dict(zip(label_mappings_etbert, probabilities))

    return dataset_predictions

# ------------------------------
# PROCESS LOGITS to proba
# ------------------------------


if __name__=='__main__':
    packet=["c1d8 d805 0562 62b9 b95b 5b10 10d4 d46d 6db5 b51e 1e66 6655 553d 3d7d 7dd9 d9a6 a6bb bbdd ddbf bf1c 1ce3 e36e 6e86 86ea eace ce65 65a0 a0a5 a527 274b 4bd3 d376 7612 1204 047b 7bcf cf77 77cc cc96 964b 4bdc dc7f 7fd8 d866 666e 6e76 7622 22d1 d1a4 a477 7717 171c 1cf3 f3a6 a68f 8fa4 a4df dfd3 d3f4 f494 948b 8b5c 5c57 577e"]
    packet2=["1069 690f 0f49 4909 0904 049e 9e1c 1c4a 4a57 5750 5010 1001 01f3 f3fe fe0a 0a00 0000 0047 4781 8181 810e 0eeb ebc1 c16e 6ef2 f2dc dc76 76cb cba6 a618 188e 8e66 66f4 f45d 5d7c 7c4f 4f7d 7dab abe1 e118 1846 4659 59e0 e089 894b 4b37 3758 5877 7704 04b3 b3de de34 3427 27da da61 6121 2182 8235 35a0 a0de de58 58a8 a8de de65"]
    proba= lstm_inference(packet)
    best_confidence=0
    best_class=""
    for class_name, confidence in proba.items():
        if confidence > best_confidence:
            best_confidence = confidence
            best_class = class_name
    print(best_class)
    print(best_confidence)
    

