import torch
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
from transformer_model import TransformerAutoencoder
from ai_engine.dataset_prep import create_sequences, SEQ_LENGTH, NUM_FEATURES

# Cấu hình
MIXED_DATA_PATH = '../data/raw/mixed_traffic_test.csv' # File có cột 'label' (0: Normal, 1: Attack)
MODEL_PATH = '../models/transformer_ae.pth'
SCALER_PATH = '../models/scaler.pkl'

def main():
    # 1. Load Scaler và Model
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
        
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = TransformerAutoencoder(num_features=NUM_FEATURES).to(device)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.eval()

    # 2. Tiền xử lý dữ liệu Test
    df_test = pd.read_csv(MIXED_DATA_PATH)
    labels = df_test['label'].values # Giữ lại nhãn thực tế để đối chiếu
    features = df_test.drop(columns=['label']).values
    
    features_scaled = scaler.transform(features)
    X_test = create_sequences(features_scaled, SEQ_LENGTH)
    
    # Vì trượt cửa sổ làm mất (SEQ_LENGTH - 1) dòng đầu, ta cần cắt nhãn tương ứng
    y_test = labels[SEQ_LENGTH - 1:]
    
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)
    
    # 3. Tính Lỗi tái tạo (Reconstruction Error)
    with torch.no_grad():
        predictions = model(X_test_tensor)
        # Tính MSE cho từng sequence
        errors = torch.mean((X_test_tensor - predictions)**2, dim=[1, 2]).cpu().numpy()
        
    # 4. Tìm Threshold (Giả sử lấy lỗi của các mẫu Normal trong tập test để tính)
    normal_errors = errors[y_test == 0]
    THRESHOLD = np.percentile(normal_errors, 99) # Cấu hình độ nhạy: lấy phân vị 99%
    print(f"\n[+] NGƯỠNG PHÁT HIỆN (THRESHOLD): {THRESHOLD:.6f}")

    # --- THÊM 3 DÒNG NÀY VÀO ---
    with open('../models/threshold.txt', 'w') as f:
        f.write(str(THRESHOLD))
    print("Đã lưu Threshold tự động vào ../models/threshold.txt")
    
    # 5. Phân loại và Đánh giá
    y_pred = (errors > THRESHOLD).astype(int)
    
    print("\n--- BÁO CÁO PHÂN LOẠI (CLASSIFICATION REPORT) ---")
    print(classification_report(y_test, y_pred, target_names=['Normal (0)', 'DDoS/Zero-day (1)']))
    
    # 6. Vẽ biểu đồ (Đưa cái này vào Báo cáo Đồ án)
    plt.figure(figsize=(10, 6))
    sns.histplot(errors[y_test == 0], bins=50, color='blue', alpha=0.6, label='Lưu lượng Bình thường')
    sns.histplot(errors[y_test == 1], bins=50, color='red', alpha=0.6, label='Tấn công DDoS')
    plt.axvline(x=THRESHOLD, color='black', linestyle='--', label=f'Ngưỡng (Threshold: {THRESHOLD:.4f})')
    
    plt.title('Phân phối Lỗi tái tạo (Reconstruction Error)')
    plt.xlabel('Mean Squared Error')
    plt.ylabel('Tần suất')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    os.makedirs('../docs', exist_ok=True) # Lưu ảnh báo cáo
    plt.savefig('../docs/error_distribution.png')
    print("Đã lưu biểu đồ phân phối lỗi tại: ../docs/error_distribution.png")

if __name__ == "__main__":
    main()