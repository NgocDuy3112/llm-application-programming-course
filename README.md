# Notes

Cấu trúc thư mục con trong thư mmục modules:

```
modules/
├── module-1/                       # Thư mục gốc của module-1
    ├── README.md                       # Tệp Markdown hướng dẫn cho mỗi module, không bắt buộc
    ├── notebooks/                      # Thư mục chứa các notebook Jupyter
    ├── chatbot/                        # Thư mục chứa mã nguồn ứng dụng
        ├── configs/                        # Thư mục chứa các tệp cấu hình
            ├── .env.example                    # Tệp mẫu biến môi trường
        ├── src/                        # Thư mục chứa mã nguồn chính của ứng dụng
        ├── app.py                      # Tệp chính chứa giao diện Streamlit để chạy ứng dụng
        ├── requirements.txt            # Tệp liệt kê các phụ thuộc của dự án
├── module-2/
    ├── README.md
    ├── notebooks/
    ├── chatbot/
        ├── configs/
            ├── .env.example
        ├── src/
        ├── app.py
        ├── requirements.txt
...
```