#  AI-Driven Insider Threat Detection System

 **Winner – 1st Prize at HackIITK 2025**  
 Beating 7000+ participants from BTech, MTech, and international universities  
 [View LinkedIn Post](https://www.linkedin.com/posts/harsh-khairnar-844001227_hackiitk-cybersecurity-kafka-activity-7317196462575050752-QPnH?utm_source=share&utm_medium=member_desktop&rcm=ACoAADjGe3QBIetyTYiCm6RFSPFG8dASKqbnhvk)

---

##  Project Overview

**AI-Driven Insider Activity Detection System** is an end-to-end AI + cybersecurity solution designed to detect, monitor, and report insider threats in real-time. It combines packet-level data analysis, machine learning models, and an interactive dashboard for analysts.

---

##  Core Objectives

1. **Robust AI-based detection** of insider threats from activity logs and network packets.
2. **Real-time, intuitive dashboard** for cybersecurity teams and SOCs.
3. **Automated report generation** and alert system for threat response.

---

##  Key Features

###  Real-Time Detection
- **Packet Sniffing**: Using `Scapy` for live network capture.
- **Streaming & Buffering**: Handled via `Apache Kafka` for scalable data ingestion.
- **XGBoost Model**: Fast binary classification of anomalous activity from packet batches (aggregated every 50 packets).

###  Deep Anomaly Detection
- **Autoencoder Neural Network**: Trained on random sample of 13GB+ of engineered insider activity data for hidden pattern recognition.
- **Dask**: Used for parallelized data handling and feature engineering on Google Colab (T4 GPU).

###  Email Threat Analysis
- **VirusTotal API**: Scans email payloads and attachments to flag known malware and phishing attempts.

---

## 📊 Interactive Dashboard (Next.js)

- Real-time threat alerts with color-coded severity.
- Downloadable `.pcap` logs for forensic analysis.
- Incident tracking & analyst assignment.
- Timeline visualizations of suspicious user behavior.
- Clean UI/UX for Security Operations Centers (SOC).

---

## 🛠 Tech Stack

| Component         | Technology         |
|------------------|--------------------|
| Packet Capture    | Scapy              |
| Stream Processing | Apache Kafka       |
| AI Models         | XGBoost, Autoencoder |
| Dashboard         | Next.js (React)    |
| Backend/API       | FastAPI            |
| Data Processing   | Dask, Pandas       |
| Email Scanning    | VirusTotal API     |
| Hosting/Infra     | Google Colab (GPU) |

---

## 🚧 Challenges & Solutions

| Challenge                                 | Solution                                  |
|------------------------------------------|-------------------------------------------|
| High-volume feature engineering          | Dask + Colab T4 GPU for parallel processing |
| Packet flood handling in real time       | Aggregated analysis per 50 packets         |
| Usability for analysts                   | Built modular and responsive Next.js dashboard |

---

## 🧪 Setup Instructions (Basic)

```bash
# Clone the repo
git clone https://github.com/khairnarhg/insider-threat-detection.git
cd insider-threat-detection

# Start backend (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Start frontend (Next.js)
cd ../dashboard
npm install
npm run dev
