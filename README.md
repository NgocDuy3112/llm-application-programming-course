# Notes

Cấu trúc thư mục con trong thư mục modules:

```
modules/
├── module-1/
├── module-2/
├── module-3/
├── module-4/
├── module-5/
│   ├── demos/                      # Mã nguồn chạy demo trong giờ học
│   │   ├── model/                  # Tầng truy cập dữ liệu (API Adapter)
│   │   ├── orchestrator/           # Tầng điều phối logic
│   │   ├── ui/                     # Tầng giao diện người dùng
│   │   ├── 01-demo.py
│   │   ├── 02-demo.py 
│   │   └── ...             
│   ├── exercises/                  # Bài tập tự thực hành (Starter Code)
│   │   ├── model/
│   │   ├── orchestrator/
│   │   ├── ui/
│   │   └── app.py                  # File chính để chạy bài tập
│   ├── solution/                   # Đáp án hoàn chỉnh của module
│   │   ├── model/
│   │   ├── orchestrator/
│   │   ├── ui/
│   │   └── app.py  
│   ├── README.md
│   ├── requirements.txt
│   └── .env.example
├── module-6-7/
├── module-8-9/
...
```