import os
from tqdm import tqdm
import subprocess

def rename_pcap_files():
    filenames = os.listdir("D:/freelance/upwork_aamina/dataset/pcap/ISCXVPN2016")
    for filename in tqdm(filenames):
        new_filename = filename.strip(" ")
        os.rename(os.path.join("D:/freelance/upwork_aamina/dataset/pcap/ISCXVPN2016", filename), 
                 os.path.join("D:/freelance/upwork_aamina/dataset/pcap/ISCXVPN2016", new_filename))

def split_pcap_files():
    splitter = "D:/freelance/upwork_aamina/ShieldGPT/ShieldGPT/pcap_tool/splitter.exe"
    label_dict = {
        "browsing": ["vpn_netflix", "vpn_spotify", "vpn_voipbuster"],
        "email": ["vpn_email"],
        "chat": ["vpn_icq_chat", "vpn_aim_chat", "vpn_skype_chat", "vpn_facebook_chat", "vpn_hangouts_chat"],
        "streaming": ["vpn_vimeo", "vpn_youtube"],
        "ftp": ["vpn_ftp", "vpn_sftp", "vpn_skype_files"],
        "voip": ["vpn_skype_audio", "vpn_facebook_audio", "vpn_hangouts_audio"],
        "p2p": ["vpn_bittorrent"]
    }

    for label, value_list in label_dict.items():
        filenames = []
        for value in value_list:
            filenames += list(filter(lambda x: x.endswith("pcap") and x.startswith(value), 
                            os.listdir("D:/freelance/upwork_aamina/dataset/pcap/ISCXVPN2016"))) # only consider VPN traffic, ignore NonVPN
        filenames = [f"D:/freelance/upwork_aamina/dataset/pcap/ISCXVPN2016/{x}" for x in filenames]
        for filename in tqdm(filenames):
           # print(filename) #for debugging
            dir_name = os.path.join("D:/freelance/upwork_aamina/dataset/pcap/ISCXVPN2016/flows", label)
            os.makedirs(dir_name, exist_ok=True)
            flow_prefix = os.path.basename(filename)[:-len(".pcap")]
            with open(os.path.join("D:/freelance/upwork_aamina/dataset/pcap/ISCXVPN2016/flows", f"{flow_prefix}.log"), "w") as f:
                subprocess.run(f"{splitter} -i '{filename}' -o '{dir_name}' -p {flow_prefix} -f five_tuple -h",
                            shell=True, stdout=f, stderr=subprocess.STDOUT)

if __name__ == "__main__":
    # rename_pcap_files()
    split_pcap_files()