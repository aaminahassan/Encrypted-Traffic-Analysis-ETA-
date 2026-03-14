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

# NetMamba-Based Encrypted Traffic Classification Framework

## 1. Title
Evaluating the Robustness of NetMamba and YaTC for Encrypted Traffic Analysis Across Heterogeneous Network Datasets

This repository contains the implementation used in the research study evaluating modern deep learning architectures for Encrypted Traffic Classification (ETC). The implementation focuses on the NetMamba architecture and supporting scripts used for dataset preparation, model training, and evaluation.

---

# 2. Description
This repository provides the code and environment configuration required to reproduce the experiments described in the research paper.

The framework implements deep learning models for encrypted traffic classification using side‑channel network features extracted from encrypted flows. The repository includes:

- Model implementation (NetMamba architecture)
- Dataset preprocessing scripts
- Training and evaluation pipeline
- Dependency configuration for reproducible experiments

The goal of the project is to evaluate how modern sequence‑model architectures perform when classifying encrypted network traffic across heterogeneous datasets.

---

# 3. Dataset Information

The experiments use publicly available encrypted traffic datasets commonly used in network security research.

Datasets Used:

CICIoT2022 – IoT network traffic dataset containing benign and attack traffic  
ISCXVPN2016 – VPN vs non‑VPN encrypted traffic dataset  
ISCXTor2016 – Tor vs non‑Tor traffic classification dataset  
USTC‑TFC2016 – Traffic classification dataset with encrypted application flows  
CSTNET‑TLS1.3 – TLS 1.3 encrypted traffic dataset used for modern encrypted traffic analysis

Datasets can be downloaded from their respective public repositories. Dataset preprocessing scripts are provided in the repository to convert raw traffic features into the format required for model training.

---

# 4. Code Information

Repository Structure:

NetMamba/
│
├── data/
│   ├── preprocessing scripts
│   └── dataset loaders
│
├── models/
│   └── NetMamba implementation
│
├── training/
│   └── training scripts
│
├── evaluation/
│   └── evaluation and metrics scripts
│
├── requirements.txt
└── README.md

Key components include:

NetMamba Model Implementation – State space model architecture used for encrypted traffic classification  
Dataset Loader – Scripts for loading and preprocessing datasets  
Training Pipeline – Model training and evaluation framework  
Metrics Module – Calculates accuracy, precision, recall, and F1‑score

---

# 5. Usage Instructions

Step 1: Install Windows Subsystem for Linux (WSL2)

Open PowerShell as Administrator and run:

wsl --install Ubuntu

---

Step 2: Install Miniconda

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

Restart terminal and verify installation:

conda --version

---

Step 3: Create Python Environment

conda create -n NetMamba python=3.10.13
conda activate NetMamba

---

Step 4: Install PyTorch

pip install torch==2.1.1 torchvision==0.16.1 --index-url https://download.pytorch.org/whl/cu121

---

Step 5: Install NumPy

pip install numpy==1.26.2

---

Step 6: Install libtinfo5

sudo apt update
wget http://security.ubuntu.com/ubuntu/pool/universe/n/ncurses/libtinfo5_6.3-2ubuntu0.1_amd64.deb
sudo apt install ./libtinfo5_6.3-2ubuntu0.1_amd64.deb

---

Step 7: Install CUDA Toolkit

wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-1
source ~/.bashrc

---

Step 8: Install GCC Compiler

sudo apt install -y gcc-12 g++-12

export CC=gcc-12
export CXX=g++-12
export CUDAHOSTCXX=g++-12

---

Step 9: Configure SSH Key for GitHub

ssh-keygen -t ed25519 -C "your_email@example.com"

Print the key:

cat ~/.ssh/id_ed25519.pub

Add the generated key to your GitHub account.

---

Step 10: Clone Repository

git clone git@github.com:itashiUchiha/upwork_Aaminaa.git

---

Step 11: Install NetMamba

cd /upwork_Aaminaa/web_app/back/data/github_repo/NetMamba/mamba-1p1p1
pip install --no-build-isolation .

Install remaining dependencies:

cd ..
pip install --no-build-isolation -r requirements.txt

---

# 6. Requirements

Software Requirements:

Python 3.10.13  
PyTorch 2.1.1  
CUDA Toolkit 12.1  
NumPy 1.26.2  
GCC 12  

Hardware Requirements:

GPU recommended (NVIDIA CUDA compatible)  
Minimum 16 GB RAM recommended

---

# 7. Methodology

1. Dataset Collection  
Public encrypted traffic datasets are collected from research repositories.

2. Data Preprocessing  
Traffic flows are converted into structured sequences of packet-level features.

3. Feature Representation  
Side-channel features such as packet size, timing patterns, and flow statistics are extracted.

4. Model Training  
The NetMamba model is trained using supervised learning on labeled traffic datasets.

5. Evaluation  
Models are evaluated using standard classification metrics including:
Accuracy
Precision
Recall
F1-score

6. Cross-Dataset Evaluation  
Performance is compared across multiple datasets to assess model robustness.

---

# 8. Citations

If you use this code in academic work, please cite:

Hassan, A., et al. "Evaluating the Robustness of NetMamba and YaTC for Encrypted Traffic Analysis Across Heterogeneous Network Datasets."

---

# 9. License

This project is released for research and academic purposes.

---

# 10. Contribution Guidelines

Contributions to improve reproducibility, documentation, and experimental pipelines are welcome.

Examples:
- Dataset loaders
- Model improvements
- Experiment automation scripts
- Documentation updates


