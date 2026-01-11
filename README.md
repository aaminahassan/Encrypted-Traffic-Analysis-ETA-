# Encrypted Traffic Classification  Model Comparison

This Kaggle notebook presents a **comparative performance analysis** of four deep learning models for **Encrypted Traffic Analysis (ETA)**:

- **LSTM**
- **ET-BERT**
- **YaTC**
- **NetMamba**

The objective is to evaluate how different sequence modeling paradigms perform when classifying encrypted network traffic **without decrypting packet payloads**, ensuring privacy preservation.

---

## Motivation
The widespread adoption of **TLS 1.3, QUIC, and Encrypted Client Hello (ECH)** has rendered traditional Deep Packet Inspection (DPI) ineffective.  
This work explores **learning-based traffic classification** approaches that rely on flow behavior rather than payload visibility.

---

## Datasets Used (with Official Links)
This notebook evaluates models across **four widely-used public benchmark datasets** for encrypted traffic classification:

###  ISCX VPN Dataset
- **Provider:** Canadian Institute for Cybersecurity (CIC), University of New Brunswick  
- **Description:** Encrypted VPN and non-VPN traffic for application classification  
- **Link:** https://www.unb.ca/cic/datasets/vpn.html

---

###  ISCX Tor Dataset
- **Provider:** Canadian Institute for Cybersecurity (CIC), University of New Brunswick  
- **Description:** Encrypted Tor traffic representing anonymity-preserving applications  
- **Link:** https://www.unb.ca/cic/datasets/tor.html

---

###  CIC IoT Dataset 2022
- **Provider:** Canadian Institute for Cybersecurity (CIC), University of New Brunswick  
- **Description:** Large-scale IoT network traffic including encrypted communication patterns  
- **Link:** https://www.unb.ca/cic/datasets/iotdataset-2022.html

---

### USTC-TFC2016 Dataset
- **Provider:** University of Science and Technology of China (USTC)  
- **Description:** Fine-grained encrypted traffic flows for application-level classification  
- **Link:** https://github.com/davidyslu/USTC-TFC2016

> ✅ These datasets collectively cover **VPN, Tor, IoT, and general encrypted traffic**, making them suitable for robust and cross-domain ETA benchmarking.

---

## Methodology
The notebook follows a unified experimental pipeline:

1. **Data Preprocessing**
   - Feature normalization and sequence construction
   - Dataset-specific train/test splits

2. **Model Architectures**
   | Model | Core Principle |
   |------|---------------|
   | **LSTM** | Sequential dependency modeling |
   | **ET-BERT** | Transformer-based contextual encoding |
   | **YaTC** | Lightweight encoder optimized for traffic classification |
   | **NetMamba** | State-space modeling for long-range dependencies |

3. **Evaluation Metrics**
   - Accuracy
   - Precision
   - Recall
   - F1-score
   - Confusion Matrix Analysis

---

## Results Summary
Key observations:

- **YaTC and NetMamba outperform LSTM and ET-BERT** across datasets
- Improved diagonal dominance in confusion matrices
- Better scalability for long encrypted flows
- Reduced computational overhead compared to transformer models

---

## Libraries & Tools
```text
Python 3.x
NumPy
Pandas
Scikit-learn
PyTorch / TensorFlow
Matplotlib
Seaborn



