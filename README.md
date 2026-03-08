# DDoS-Defense-System

## Sơ đồ cấu trúc thư mục (Directory Tree)
DDoS-Defense-System/
│
├── data/                       # Thư mục chứa dữ liệu (Không push lên Git)
│   ├── raw/                    # Chứa file log gốc xuất ra từ Snort/Elasticsearch
│   └── processed/              # Chứa file .csv đã qua tiền xử lý, gộp chuỗi (Windowing)
│
├── models/                     # Thư mục lưu trữ mô hình AI đã huấn luyện
│   ├── transformer_ae.pth      # File trọng số (weights) của Transformer
│   └── scaler.pkl              # File lưu bộ chuẩn hóa (MinMaxScaler) để scale dữ liệu real-time
│
├── training/                   # 💻 KHU VỰC CỦA NHÓM AI (Huấn luyện mô hình)
│   ├── dataset_prep.py         # Code đọc log, trích xuất 20 features, chia sequence (Sliding Window)
│   ├── transformer_model.py    # Class định nghĩa mạng Transformer Autoencoder (Multi-head, PE)
│   ├── train.py                # Script chạy vòng lặp huấn luyện trên dữ liệu Normal
│   └── evaluate.py             # Script chạy test, vẽ biểu đồ phân phối lỗi và tính Threshold
│
├── api/                        # 💻 KHU VỰC CỦA NHÓM AI (Triển khai Microservice)
│   ├── main.py                 # File chạy server FastAPI (Tạo API endpoint nhận dữ liệu)
│   ├── predictor.py            # Code load file .pth, tính Anomaly Score và so sánh Threshold
│   └── requirements.txt        # Danh sách thư viện Python (torch, fastapi, uvicorn, pandas...)
│
├── configs/                    # 💻 KHU VỰC CỦA NHÓM MẠNG & HỆ THỐNG
│   ├── snort/                  
│   │   └── local.rules         # Các luật Snort tĩnh để chặn DDoS cơ bản, XSS, SQLi
│   ├── logstash/               
│   │   └── snort_pipeline.conf # File cấu hình Grok filter để parse log Snort đẩy vào Elasticsearch
│   └── elasticsearch/
│       └── elasticsearch.yml   # File cấu hình cluster ELK
│
├── scripts/                    # 💻 KHU VỰC CỦA NHÓM MẠNG & HỆ THỐNG (Tự động hóa)
│   ├── 01_setup_iptables.sh    # Script bash thiết lập Iptables rate-limit ban đầu (chạy trên Fedora/Linux)
│   ├── 02_start_services.sh    # Script khởi động đồng loạt Snort, ELK và FastAPI
│   └── 03_block_ip.sh          # Script nhận IP từ API và tự động thêm rule DROP vào Iptables
│
├── notebooks/                  # (Tùy chọn) Chứa file Jupyter Notebook (.ipynb) để nháp, vẽ biểu đồ
│
└── README.md                   # Tài liệu hướng dẫn cài đặt, thứ tự chạy các file cho hội đồng xem