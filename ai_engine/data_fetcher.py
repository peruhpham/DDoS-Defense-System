from elasticsearch import Elasticsearch
import pandas as pd

# 1. Kết nối vào Elasticsearch của team Hệ thống (thay bằng IP thực tế của Lab)
es = Elasticsearch("http://localhost:9200")

# 2. Query lấy toàn bộ log mạng BÌNH THƯỜNG (Giả sử lấy trong 2 tiếng qua)
query = {
    "query": {
        "match_all": {} # Tạm thời lấy hết. Thực tế có thể lọc theo thời gian
    },
    "_source": ["tcp_flags", "ip_ttl", "packet_size", "src_port", "dst_port"] # Chọn đúng 20 features bạn cần
}

print("Đang kéo log từ Elasticsearch...")
# Dùng scroll API nếu dữ liệu lớn hơn 10.000 dòng
response = es.search(index="snort-logs-*", body=query, size=10000)

# 3. Đổ dữ liệu vào Pandas DataFrame
data = [doc['_source'] for doc in response['hits']['hits']]
df_train = pd.DataFrame(data)

print(f"Đã kéo về {len(df_train)} dòng log.")
# Lưu lại thành file CSV nội bộ để team AI dễ dàng train nhiều lần mà không cần query lại
df_train.to_csv("../data/raw/normal_traffic.csv", index=False)