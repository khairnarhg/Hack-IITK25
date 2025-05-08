import pickle
import pandas as pd
import scapy.all as scapy
import re
from datetime import datetime

# --- Global Aggregators for Batching ---
batch_candidates = []
batch_packet_infos = []  # (Optional) Additional logging details.

candidate_features = [
    "FTP Detected",
    "Protocol Mismatch",
    "Multiple Login Attempts",
    "Large Packets"
]

prediction_summary = {0: 0, 1: 0}

def detect_large_packets(pkt_len, threshold=1000):
    return 1 if pkt_len > threshold else 0

def extract_http_fields(raw_payload):
    text = raw_payload.decode(errors='ignore')
    method, url, host, user_agent = None, None, None, None
    request_line_match = re.search(r"^(GET|POST|PUT|DELETE|OPTIONS|HEAD)\s+(\S+)\s+HTTP", text)
    if request_line_match:
        method = request_line_match.group(1)
        url = request_line_match.group(2)
    host_match = re.search(r"Host:\s*([^\r\n]+)", text)
    if host_match:
        host = host_match.group(1)
    user_agent_match = re.search(r"User-Agent:\s*([^\r\n]+)", text)
    if user_agent_match:
        user_agent = user_agent_match.group(1)
    return method, url, host, user_agent

def extract_packet_info(packet):
    pkt_len = len(packet)
    packet_info = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Packet Length": pkt_len,
        "Source IP": packet[scapy.IP].src if packet.haslayer(scapy.IP) else None,
        "Destination IP": packet[scapy.IP].dst if packet.haslayer(scapy.IP) else None,
        "Protocol": packet[scapy.IP].proto if packet.haslayer(scapy.IP) else None,
        "IP Flags": str(packet[scapy.IP].flags) if packet.haslayer(scapy.IP) else None,
        "Source Port": packet.sport if packet.haslayer(scapy.TCP) or packet.haslayer(scapy.UDP) else None,
        "Destination Port": packet.dport if packet.haslayer(scapy.TCP) or packet.haslayer(scapy.UDP) else None,
        "TCP Flags": str(packet[scapy.TCP].flags) if packet.haslayer(scapy.TCP) else None,
        "Host (HTTP)": None,
        "User-Agent (HTTP)": None,
        "Request Method (HTTP)": None,
        "URL": None,
        "DNS Queries": packet[scapy.DNS].qd.qname.decode() if packet.haslayer(scapy.DNS) and packet[scapy.DNS].qd else None,
        "FTP Detected": 1 if packet.haslayer(scapy.TCP) and (packet.sport == 21 or packet.dport == 21) else 0,
        "Protocol Mismatch": 1 if packet.haslayer(scapy.TCP) and packet.haslayer(scapy.UDP) else 0,
        "Multiple Login Attempts": 1 if packet.haslayer(scapy.Raw) and b"login" in packet[scapy.Raw].load.lower() else 0,
        "Large Packets": detect_large_packets(pkt_len),
    }
    
    if packet.haslayer(scapy.Raw):
        try:
            raw_data = packet[scapy.Raw].load
            method, url, host, user_agent = extract_http_fields(raw_data)
            packet_info["Request Method (HTTP)"] = method
            packet_info["URL"] = url
            packet_info["Host (HTTP)"] = host
            packet_info["User-Agent (HTTP)"] = user_agent
        except Exception as e:
            print("Error parsing HTTP fields:", e)
    
    print("Extracted packet info:", packet_info)
    return packet_info


model_filename = "F:\\HackIIT\\theproject\\insider\\server\\models\\xgboost_modelanuj3.pkl"
with open(model_filename, "rb") as f:
    model_pipeline = pickle.load(f)

def process_and_classify(packet):
    global batch_candidates, batch_packet_infos, prediction_summary

    info = extract_packet_info(packet)
    candidate = {feat: (1 if info.get(feat, 0) else 0) for feat in candidate_features}

    batch_candidates.append(candidate)
    batch_packet_infos.append(info)

    print(f"Packet added to batch. Current batch size: {len(batch_candidates)}")

    if len(batch_candidates) < 50:
        return None  # Wait until 50 packets are collected

    # Aggregate candidate features from the batch.
    aggregated = {}
    for feat in candidate_features:
        total = sum(item[feat] for item in batch_candidates)
        if feat == "Multiple Login Attempts":
            aggregated[feat] = 1 if total >= 2 else 0
        elif feat == "Large Packets":
            aggregated[feat] = 1 if total >= 2 else 0
        else:
            aggregated[feat] = 1 if total >= 1 else 0

    print("Aggregated candidate features:", aggregated)

    # Save the 50 captured packets before resetting.
    captured_packets = batch_packet_infos.copy()

    # Reset the batch accumulators.
    batch_candidates = []
    batch_packet_infos = []

    # Determine prediction using aggregated features.
    if aggregated["Multiple Login Attempts"] == 1:
        pred = 1
        print("Multiple Login Attempts threshold met. Overriding prediction to 1.")
    else:
        df_candidate = pd.DataFrame([aggregated], columns=candidate_features)
        pred = model_pipeline.predict(df_candidate)[0]
        pred = int(pred)
        print("Model prediction based on aggregated features:", pred)

    prediction_summary[pred] += 1

    # Build a batch object that includes all 50 packet infos.
    batch_log = {
        "Batch Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Total Packets": 50,
        "Packets": captured_packets,  # List of 50 packet info objects
        "Aggregated Features": aggregated,
        "Prediction": pred
    }
    print(f"Batch log: {batch_log}")
    return batch_log

