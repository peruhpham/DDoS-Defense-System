import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import MinMaxScaler
import os

# Cấu hình đường dẫn
RAW_DATA_PATH = '../data/raw/normal_traffic.csv' # File log chỉ chứa dữ liệu bình thường
PROCESSED_DATA_PATH = '../data/processed/X_train_normal.npy'
SCALER_PATH = '../models/scaler.pkl'

SEQ_LENGTH = 10 # Số gói tin trong 1 chuỗi (Cửa sổ thời gian)
NUM_FEATURES = 20 # 20 đặc trưng đã chọn lọc

def create_sequences(data, seq_length):
    """Hàm trượt cửa sổ tạo chuỗi dữ liệu"""
    sequences = []
    for i in range(len(data) - seq_length + 1):
        seq = data[i : i + seq_length]
        sequences.append(seq)
    return np.array(sequences)

def main():
    print("Đang đọc dữ liệu thô...")
    # Giả sử file csv có 20 cột đặc trưng dạng số
    df = pd.read_csv(RAW_DATA_PATH)
    
    # 1. Chuẩn hóa dữ liệu
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df.values)
    
    # Lưu bộ Scaler lại cho lúc chạy Real-time
    os.makedirs('../models', exist_ok=True)
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)
    print("Đã lưu bộ Scaler tại:", SCALER_PATH)

    # 2. Tạo chuỗi (Sequences)
    X_train = create_sequences(data_scaled, SEQ_LENGTH)
    
    # Lưu numpy array để file train.py load cho nhanh
    os.makedirs('../data/processed', exist_ok=True)
    np.save(PROCESSED_DATA_PATH, X_train)
    print(f"Hoàn tất! Kích thước tập huấn luyện: {X_train.shape}")

if __name__ == "__main__":
    main()