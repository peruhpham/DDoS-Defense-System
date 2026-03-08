#!/bin/bash

# Khai báo màu sắc cho terminal đẹp và dễ nhìn
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Không màu

echo -e "${YELLOW}=====================================================${NC}"
echo -e "${YELLOW}    BẮT ĐẦU QUY TRÌNH HUẤN LUYỆN AI TỰ ĐỘNG 🚀     ${NC}"
echo -e "${YELLOW}=====================================================${NC}"

# 1. Kiểm tra vị trí đứng (Phải đứng ở thư mục gốc)
if [ ! -d "ai_engine" ]; then
    echo -e "${RED}[LỖI] Vui lòng chạy script này từ thư mục gốc (DDoS-Defense-System/)${NC}"
    exit 1
fi

# 2. Kích hoạt môi trường ảo (uv)
echo -e "\n${GREEN}[1/5] Đang kích hoạt môi trường ảo...${NC}"
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo -e "${RED}[LỖI] Không tìm thấy môi trường ảo. Bạn đã chạy 'uv venv' chưa?${NC}"
    exit 1
fi

# Di chuyển vào thư mục code AI
cd ai_engine

# 3. Chạy từng file và kiểm tra lỗi (Dấu || nghĩa là nếu lỗi thì chạy lệnh phía sau)
echo -e "\n${GREEN}[2/5] Kéo dữ liệu log sạch từ Elasticsearch...${NC}"
python data_fetcher.py || { echo -e "${RED}[LỖI] Kéo dữ liệu thất bại! Dừng hệ thống.${NC}"; exit 1; }

echo -e "\n${GREEN}[3/5] Tiền xử lý dữ liệu và tạo Sequence...${NC}"
python dataset_prep.py || { echo -e "${RED}[LỖI] Tiền xử lý thất bại! Dừng hệ thống.${NC}"; exit 1; }

echo -e "\n${GREEN}[4/5] Huấn luyện mô hình Transformer... (Sẽ mất vài phút)${NC}"
python train.py || { echo -e "${RED}[LỖI] Huấn luyện thất bại! Dừng hệ thống.${NC}"; exit 1; }

echo -e "\n${GREEN}[5/5] Đánh giá và chốt Threshold...${NC}"
python evaluate.py || { echo -e "${RED}[LỖI] Đánh giá thất bại! Dừng hệ thống.${NC}"; exit 1; }

# Trở lại thư mục gốc
cd ..

echo -e "\n${YELLOW}=====================================================${NC}"
echo -e "${GREEN}  🎉 HOÀN TẤT QUY TRÌNH HUẤN LUYỆN THÀNH CÔNG! 🎉  ${NC}"
echo -e "${YELLOW}=====================================================${NC}"
echo -e "Hệ thống đã sẵn sàng. Để bật khiên bảo vệ thời gian thực, hãy chạy lệnh:"
echo -e "👉  ${GREEN}source .venv/bin/activate && cd ai_engine && python realtime_detector.py${NC}\n"