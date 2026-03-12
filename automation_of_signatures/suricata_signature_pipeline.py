import json
import os
import paramiko
from datetime import datetime

# ---------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------

SURICATA_HOST = os.getenv("SURICATA_HOST")
SURICATA_PORT = int(os.getenv("SURICATA_PORT", 22))

REMOTE_RULE_PATH = "/etc/suricata/rules/eta_auto.rules"

LOCAL_RULE_FILE = "generated_suricata.rules"

INDICATOR_LOG = "eta_indicators.json"

SID_START = 900000


# ---------------------------------------------------
# LOAD INDICATORS FROM ETA LOG
# ---------------------------------------------------

def load_indicators():

    with open(INDICATOR_LOG, "r") as f:
        data = json.load(f)

    return data


# Example indicator format
# [
#   {"type": "ja3", "value": "72a589da586844d7f0818ce684948eea"},
#   {"type": "domain", "value": "malicious.example.com"},
#   {"type": "ip", "value": "192.168.100.45"}
# ]


# ---------------------------------------------------
# SURICATA RULE GENERATORS
# ---------------------------------------------------

def generate_ja3_rule(value, sid):

    return f"""
alert tls any any -> any any (
    msg:"ETA Detection - Suspicious JA3 {value}";
    ja3.hash; content:"{value}";
    classtype:trojan-activity;
    sid:{sid};
    rev:1;
)
""".strip()


def generate_domain_rule(value, sid):

    return f"""
alert tls any any -> any any (
    msg:"ETA Detection - Suspicious Domain {value}";
    tls.sni; content:"{value}";
    classtype:trojan-activity;
    sid:{sid};
    rev:1;
)
""".strip()


def generate_ip_rule(value, sid):

    return f"""
alert ip any any -> {value} any (
    msg:"ETA Detection - Suspicious IP {value}";
    classtype:trojan-activity;
    sid:{sid};
    rev:1;
)
""".strip()


# ---------------------------------------------------
# RULE TRANSLATION ENGINE
# ---------------------------------------------------

def generate_rules(indicators):

    rules = []
    sid = SID_START

    for ind in indicators:

        if ind["type"] == "ja3":
            rules.append(generate_ja3_rule(ind["value"], sid))

        elif ind["type"] == "domain":
            rules.append(generate_domain_rule(ind["value"], sid))

        elif ind["type"] == "ip":
            rules.append(generate_ip_rule(ind["value"], sid))

        sid += 1

    return rules


# ---------------------------------------------------
# WRITE RULE FILE
# ---------------------------------------------------

def write_rule_file(rules):

    header = f"""
# ----------------------------------------
# Zenguard Automated Rule File
# Generated: {datetime.utcnow()}
# ----------------------------------------
"""

    with open(LOCAL_RULE_FILE, "w") as f:

        f.write(header)

        for r in rules:
            f.write(r + "\n\n")


# ---------------------------------------------------
# DEPLOY RULE FILE TO SURICATA
# ---------------------------------------------------

def deploy_rules():

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=SURICATA_HOST,
        port=SURICATA_PORT
    )

    sftp = ssh.open_sftp()

    sftp.put(LOCAL_RULE_FILE, REMOTE_RULE_PATH)

    sftp.close()

    # Reload Suricata rules
    ssh.exec_command("sudo suricatactl reload-rules")

    ssh.close()

    print("Rules successfully deployed to Suricata.")


# ---------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------

def run_pipeline():

    indicators = load_indicators()

    rules = generate_rules(indicators)

    write_rule_file(rules)

    deploy_rules()


if __name__ == "__main__":
    run_pipeline()