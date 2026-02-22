from scapy.all import  rdpcap
import binascii
def cut(obj, sec):
    result = [obj[i:i+sec] for i in range(0,len(obj),sec)]
    try:
        remanent_count = len(result[0])%4
    except Exception as e:
        remanent_count = 0
        print("cut datagram error!")
    if remanent_count == 0:
        pass
    else:
        result = [obj[i:i+sec+remanent_count] for i in range(0,len(obj),sec+remanent_count)]
    return result

def bigram_generation(packet_datagram, packet_len = 64, flag=True):
    result = ''
    generated_datagram = cut(packet_datagram,1)
    token_count = 0
    for sub_string_index in range(len(generated_datagram)):
        if sub_string_index != (len(generated_datagram) - 1):
            token_count += 1
            if token_count > packet_len:
                break
            else:
                merge_word_bigram = generated_datagram[sub_string_index] + generated_datagram[sub_string_index + 1]
        else:
            break
        result += merge_word_bigram
        result += ' '
    
    return result

async def get_feature_packet(pcap_flow="./data/temp/pcaps/flow_1.pcap",payload_len=64):
    feature_data = []

    packets = rdpcap(pcap_flow)
    packet_data_string = ''  
    for packet in packets:
            packet_data = packet.copy()
            data = (binascii.hexlify(bytes(packet_data)))
            packet_string = data.decode()
            new_packet_string = packet_string[76:]
            packet_data_string += bigram_generation(new_packet_string, packet_len=payload_len, flag = True)
            break

    feature_data.append(packet_data_string)
    return feature_data

if __name__=='__main__':
    pcap_flow="./data/temp/pcaps/flow_1.pcap"
    packet=get_feature_packet(pcap_flow,payload_len=64)
    print(packet)