import time
import torch
import pickle
import pandas as pd
import numpy as np
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

# Load Model và Scaler đã train ở Bước 1
from transformer_model import TransformerAutoencoder
from dataset_prep import create_sequences, SEQ_LENGTH, NUM_FEATURES

device = torch.device('cpu')
model = TransformerAutoencoder(num_features=NUM_FEATURES).to(device)
model.load_state_dict(torch.load('../models/transformer_ae.pth'))
model.eval()

# with open('../models/scaler.pkl', 'rb') as f:
#     scaler = pickle.load(f)

# THRESHOLD = 0.045 # Ngưỡng bạn đã tìm ra ở file evaluate.py

# Xóa dòng cũ và thay bằng 2 dòng này:
with open('../models/threshold.txt', 'r') as f:
    THRESHOLD = float(f.read().strip())
print(f"[*] Đã load Threshold tự động: {THRESHOLD}")

es = Elasticsearch("http://localhost:9200")
INDEX_READ = "snort-logs-*"
INDEX_WRITE = "alerts-zeroday" # Index mới để Kibana đọc cảnh báo

def detect_anomaly():
    # 1. Lấy log của 5 giây gần nhất
    now = datetime.utcnow()
    past_5s = now - timedelta(seconds=5)
    
    query = {
        "query": {
            "range": {
                "@timestamp": { # Trường thời gian mặc định của ELK
                    "gte": past_5s.isoformat() + "Z",
                    "lt": now.isoformat() + "Z"
                }
            }
        },
        "_source": ["@timestamp", "src_ip", "tcp_flags", "ip_ttl", "packet_size"] # Các features
    }
    
    response = es.search(index=INDEX_READ, body=query, size=1000)
    hits = response['hits']['hits']
    
    if len(hits) < SEQ_LENGTH:
        return # Nếu mạng quá vắng, không đủ tạo 1 sequence (10 gói tin) thì bỏ qua
    
    # 2. Tiền xử lý dữ liệu live
    df_live = pd.DataFrame([doc['_source'] for doc in hits])
    features_only = df_live.drop(columns=['@timestamp', 'src_ip']).values
    
    scaled_data = scaler.transform(features_only)
    X_live = create_sequences(scaled_data, SEQ_LENGTH)
    X_live_tensor = torch.tensor(X_live, dtype=torch.float32)
    
    # 3. Đưa qua Transformer để tính Lỗi tái tạo (Reconstruction Error)
    with torch.no_grad():
        predictions = model(X_live_tensor)
        errors = torch.mean((X_live_tensor - predictions)**2, dim=[1, 2]).numpy()
    
    # 4. Kiểm tra Ngưỡng và Cảnh báo
    for i, error in enumerate(errors):
        if error > THRESHOLD:
            # Lấy IP nguồn của gói tin cuối cùng trong chuỗi gây ra lỗi
            malicious_ip = df_live.iloc[i + SEQ_LENGTH - 1]['src_ip']
            
            # Tạo document cảnh báo đẩy ngược lại ELK
            alert_doc = {
                "@timestamp": datetime.utcnow().isoformat() + "Z",
                "alert_type": "Zero-day/DDoS Detected",
                "src_ip": malicious_ip,
                "anomaly_score": float(error),
                "threshold": float(THRESHOLD)
            }
            # Bắn cảnh báo vào Index mới. Kibana sẽ theo dõi index này để vẽ biểu đồ đỏ
            es.index(index=INDEX_WRITE, document=alert_doc)
            print(f"[CẢNH BÁO] Phát hiện tấn công từ IP: {malicious_ip} | Score: {error:.4f}")
            
            # (Tùy chọn) Tại đây có thể gọi hàm chạy lệnh bash 'iptables -A INPUT -s {malicious_ip} -j DROP'

if __name__ == "__main__":
    print("Khởi động hệ thống AI giám sát Real-time...")
    while True:
        detect_anomaly()
        time.sleep(5) # Quét mỗi 5 giây