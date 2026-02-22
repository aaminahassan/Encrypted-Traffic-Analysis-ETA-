from typing import Dict, Any, List
from scipy.special import softmax

# Configuration
CONFIDENCE_THRESHOLD = 0.0
CONFIDENCE_THRESHOLD_lstm = 0.20

DATASETS = ["USTC_TFC2016", "CICIOT2022", "ISCX_VPN2016", "ISCX_TOR2016"]

def packet_stat(packets):
# Convert Scapy's summary string to a dict
#packets=rdpcap("/content/echdot1LOCALVOLUMEOFF_1.pcap")
    summary_str = str(packets)  # "<1.pcap: TCP:17 UDP:0 ICMP:0 Other:0>"
    summary_str = summary_str.strip("<>").split(": ", 1)[1]  # remove <1.pcap:
    items = summary_str.split(" ")
    protocol_counts = {}
    for item in items:
        proto, count = item.split(":")
        protocol_counts[proto] = int(count)
    protocol_counts
    return protocol_counts



def aggregate_model_predictions(all_predictions):
    model_results = {}
    
    for model_name, class_probabilities in all_predictions.items():
        # Find the best prediction across all datasets
        best_class = None
        best_confidence = 0.0
        
        for class_name, confidence in class_probabilities.items():
            if confidence > best_confidence:
                best_confidence = confidence
                best_class = class_name
        
     
        model_results[model_name] = {
            "prediction": best_class if best_confidence >= CONFIDENCE_THRESHOLD else "unknown",
            "confidence": float(best_confidence)
        }
    
    # Determine final decision
    high_confidence_count = sum(
        1 for result in model_results.values() 
        if result["confidence"] >= CONFIDENCE_THRESHOLD
    )
    
    final_decision = (
        "belongs_to_known_dataset" 
        if high_confidence_count >= 1  # At least 2 models agree
        else "not_part_of_any_dataset"
    )
    
    return {
        **model_results,
        "final_decision": final_decision
    }

