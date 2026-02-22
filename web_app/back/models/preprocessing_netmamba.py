from scapy.all import rdpcap,wrpcap
import os 
import json
import shutil
import numpy as np
import binascii
from PIL import Image
def tranform_to_img(file):
    #read the file  and give the number of flow 
    #split the file in different flow and store it in a temp folder 
    #take one flow and do the necessary processing
    #feed to the model 
    pass
# a flow is categorized by their 5-tuple attributes: Source IP, Destination IP, Source Port, Destination Port, and Protocol

async def split_pcap_file_single2(packets):
    """
    Split PCAP into flows and save the first flow with at least 5 packets.
    Returns: dict with 'success' or 'error' key
    """
    # This dictionary will store the packets for each flow.
    flows = {}
    
    # Iterate through each packet just once.
    for pkt in packets:
        # We only care about IP packets with a TCP or UDP layer.
        if "IP" in pkt and ("TCP" in pkt or "UDP" in pkt):
            
            ip_layer = pkt["IP"]
            flow_key = (ip_layer.src, ip_layer.dst, ip_layer.proto, pkt.sport, pkt.dport)

            flow_packets = flows.setdefault(flow_key, [])

            if len(flow_packets) < 5:
                flow_packets.append(pkt)
            elif len(flow_packets) == 5:
                print("one flow is complete")
                pcap_dir = "./data/temp/pcaps/"
                if os.path.exists(pcap_dir):
                    print("inside the if")
                    shutil.rmtree(pcap_dir)
                    os.makedirs(pcap_dir, exist_ok=True)
                else:
                    print("inside the else")
                    os.makedirs(pcap_dir, exist_ok=True)

                filename = f"./data/temp/pcaps/flow_1.pcap"
                wrpcap(filename, flow_packets)
                
                return {"success": True, "number_of_flows": len(flows)}
                break

            if flow_key not in flows and len(flows) >= 5:
                flows.pop(flow_key)
                continue
    
    # If we reach here, no flow had at least 5 packets
    return {"error": "No network flow contains at least 5 packets"}

async def split_pcap_file_single(packets, max_packets_per_flow=5, max_flows=5):
    pcap_dir = "./data/temp/pcaps/"

    # ✅ Reset folder ONCE
    if os.path.exists(pcap_dir):
        shutil.rmtree(pcap_dir)
    os.makedirs(pcap_dir, exist_ok=True)

    flows = {}
    flow_index = 0

    for pkt in packets:
        if "IP" in pkt and ("TCP" in pkt or "UDP" in pkt):
            ip = pkt["IP"]
            flow_key = (ip.src, ip.dst, ip.proto, pkt.sport, pkt.dport)

            flow_packets = flows.setdefault(flow_key, [])

            if len(flow_packets) < max_packets_per_flow:
                flow_packets.append(pkt)

            if len(flow_packets) == max_packets_per_flow:
                filename = os.path.join(
                    pcap_dir, f"flow_{flow_index}.pcap"
                )
                wrpcap(filename, flow_packets)
                flow_index += 1

                if flow_index >= max_flows:
                    break
    if flow_index==0:
        return {"error": "No network flow contains at least 5 packets"}


    return {"success": True, "number_of_flows": len(flows)}
async def split_pcap_file(packets):
    """
    Efficiently groups packets into flows and saves the first 5 packets
    of the first 5 flows discovered.

    Args:
        packets: A list of Scapy packets.
    """
    # This dictionary will store the packets for each flow.
    flows = {}
    
    # Iterate through each packet just once.
    for pkt in packets:
        # We only care about IP packets with a TCP or UDP layer.
        if "IP" in pkt and ("TCP" in pkt or "UDP" in pkt):
            
            # Create the unique 5-tuple key for the unidirectional flow.
            ip_layer = pkt["IP"]
            flow_key = (ip_layer.src, ip_layer.dst, ip_layer.proto, pkt.sport, pkt.dport)

            # Get the list of packets for this flow.
            # If the flow is new, setdefault creates an empty list for it.
            flow_packets = flows.setdefault(flow_key, [])

            # --- Core Optimization ---
            # Only add the packet if this specific flow has fewer than 5 packets.
            # This prevents storing thousands of unneeded packets for a single flow.
            if len(flow_packets) < 5:
                flow_packets.append(pkt)

            # --- Secondary Optimization ---
            # If we have already found 5 flows, we don't need to look for any new ones.
            # This check prevents the 'flows' dictionary from growing unnecessarily.
            # Note: We don't break the loop, as existing flows might still need to be
            # filled up to 5 packets.
            if flow_key not in flows and len(flows) >= 5:
                flows.pop(flow_key)
                continue
            
    
    #delete file present in the dir first 
    pcap_dir="./data/temp/pcaps/"
    if os.path.exists(pcap_dir):
        shutil.rmtree(pcap_dir)
        os.makedirs(pcap_dir,exist_ok=True)
    for i, (flow_key, flow_packets) in enumerate(flows.items(), 1):
        
        filename = f"./data/temp/pcaps/flow_{i}.pcap"
        wrpcap(filename, flow_packets)
        print(f"Wrote {len(flow_packets)} packets to {filename}")
    
    return {"number_of_flow":len(flows)}

def pcap_to_array(pcap_dir="./data/temp/pcaps", if_augment=False):
    assert pcap_dir.split("/")[-1] == "pcaps"
    image_dir = "./data/temp/netmamba_dataset/dummy_class"
    if os.path.exists(image_dir):
        shutil.rmtree(image_dir)
        os.makedirs(image_dir,exist_ok=True)
    else:
        os.makedirs(image_dir,exist_ok=True)
    print(image_dir)
    pcap_filenames = os.listdir(pcap_dir)
    for pcap_filename in pcap_filenames:
        try:
            if not if_augment:
                image_filename = f"{image_dir}/{pcap_filename[:-len('.pcap')]}.png"
                stat_filename = image_filename.replace(".png", ".json")
                res = read_5hp_list(f"{pcap_dir}/{pcap_filename}")[0]
                #print(res)
                flow_array = res.pop("data")
                #print(res)
                #print(flow_array[0:15])
                image = Image.fromarray(flow_array.reshape(40, 40).astype(np.uint8))
                print("saving the images")
                image.save(image_filename)
                with open(stat_filename, "w") as f:
                    json.dump(res, f)
            else:
                res_list = read_5hp_list(f"{pcap_dir}/{pcap_filename}", if_augment=True)
                for i, res in enumerate(res_list):
                    image_filename = f"{image_dir}/{pcap_filename[:-len('.pcap')]}-{i}.png"
                    stat_filename = image_filename.replace(".png", ".json")
                    flow_array = res.pop("data")
                    image = Image.fromarray(flow_array.reshape(40, 40).astype(np.uint8))
                    image.save(image_filename)
                    with open(stat_filename, "w") as f:
                        json.dump(res, f)
        except Exception as e:
            print(f"Error processing {pcap_filename}: {e}")
    
    if os.path.exists(image_dir):
        return{"images":True}
    else:
        return {"images":False}

def read_5hp_list(pcap_filename, if_augment=False, remove_ip=True, keep_payload=True):
    packets = rdpcap(pcap_filename)
    #print(packets)
    data = []
    flow_string_length = 3200
    flow_packet_num = 5
    end = len(packets) if if_augment else flow_packet_num
    for packet in packets[:end]:
        try:
            # ip = packet['IP']
            header, payload = raw_packet_to_string(packet, remove_ip=remove_ip, keep_payload=keep_payload)
            print("inside the try ")
            #print(f"header: {header}")
            #print(f"packet:{payload}")

        except:
            # continue
            header, payload = '0' * 160, '0' * 480
        data.append(header + payload)

    if not if_augment or len(data) <= flow_packet_num:
        flow_string = ''.join(data)
        flow_string += '0' * (flow_string_length - len(flow_string))
        flow_array = string_to_hex_array(flow_string)
        return [{
            "data": flow_array,
            "packet_count":len(packets)
        }]
    else:
        assert len(data) > flow_packet_num
        flow_array_list = []
        for i in range(len(data) - flow_packet_num + 1):
            flow_string = ''.join(data[i:i + flow_packet_num])
            flow_array_list.append(string_to_hex_array(flow_string))
        return [{
            "data": flow_array,
        } for flow_array in 
        zip(flow_array_list)]

def raw_packet_to_string(packet, remove_ip=True, keep_payload=True):
    ip = packet["IP"]
    if remove_ip:
        PAD_IP_ADDR = "0.0.0.0"
        ip.src, ip.dst = PAD_IP_ADDR, PAD_IP_ADDR
    header = (binascii.hexlify(bytes(ip))).decode()
    if keep_payload:
        try:
            payload = (binascii.hexlify(bytes(packet['Raw']))).decode()
            header = header.replace(payload, '')
        except:
            payload = ''
    else:
        payload = ''
    header = header[:160] if len(header) > 160 else header + '0' * (160 - len(header))
    payload = payload[:480] if len(payload) > 480 else payload + '0' * (480 - len(payload))
    return header, payload

def string_to_hex_array(flow_string):
    return np.array([int(flow_string[i:i + 2], 16) for i in range(0, len(flow_string), 2)])

if __name__=="__main__":
    pcap_to_array()