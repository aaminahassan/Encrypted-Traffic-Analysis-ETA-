#pip install gdown
import gdown
url_merge_model="https://drive.google.com/drive/folders/179Wt-1hK-g1wvhit4IRp2xL1kpbOIElF?usp=sharing" 
url_file_yatc="https://drive.google.com/file/d/1ofCK_e7nY2J0fXOtS2j89r2RnE_mkyTE/view?usp=sharing"
url_netmamba_model="https://drive.google.com/drive/folders/1a3-k3mvNl2Y7e9HbDqvjJJKcG6y7d7qQ?usp=sharing" 
url_yatc_models="https://drive.google.com/drive/folders/1TpzYssFHwyauqCpZF_o08CZg2ThqB4Ug?usp=sharing"
#gdown.download_folder(url=url_merge_model, output="./data/", quiet=False)
gdown.download(url=url_file_yatc, output="./data/finetuned_merge_models/finetuned_yatc_merge_model_small.pth", quiet=False)
#gdown.download_folder(url=url_netmamba_model, output="./data/", quiet=False)
#gdown.download_folder(url=url_yatc_models, output="./data/", quiet=False)


