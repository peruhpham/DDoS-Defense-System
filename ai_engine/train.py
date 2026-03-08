import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import os
from transformer_model import TransformerAutoencoder

# Cấu hình
PROCESSED_DATA_PATH = '../data/processed/X_train_normal.npy'
MODEL_SAVE_PATH = '../models/transformer_ae.pth'
NUM_FEATURES = 20
BATCH_SIZE = 64
EPOCHS = 50
LEARNING_RATE = 1e-3

def main():
    print("Đang nạp dữ liệu huấn luyện...")
    X_train_np = np.load(PROCESSED_DATA_PATH)
    X_train_tensor = torch.tensor(X_train_np, dtype=torch.float32)
    
    # Tạo DataLoader để chia batch
    dataset = TensorDataset(X_train_tensor, X_train_tensor) # Autoencoder: Input = Target
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    # Khởi tạo model, loss, optimizer
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = TransformerAutoencoder(num_features=NUM_FEATURES).to(device)
    
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    print(f"Bắt đầu huấn luyện trên thiết bị: {device}")
    model.train()
    
    for epoch in range(EPOCHS):
        total_loss = 0
        for batch_x, batch_y in dataloader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            
            optimizer.zero_grad()
            reconstructed = model(batch_x)
            loss = criterion(reconstructed, batch_y)
            
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        avg_loss = total_loss / len(dataloader)
        if (epoch + 1) % 5 == 0:
            print(f'Epoch [{epoch+1}/{EPOCHS}], Loss trung bình: {avg_loss:.6f}')
            
    # Lưu mô hình
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print("Huấn luyện xong! Đã lưu mô hình tại:", MODEL_SAVE_PATH)

if __name__ == "__main__":
    main()