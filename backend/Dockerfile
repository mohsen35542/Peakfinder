# ================ مرحله 1: Build ================
FROM python:3.11-slim as builder

WORKDIR /app

# نصب وابستگی‌های سیستمی
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# کپی و نصب وابستگی‌های پایتون
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ================ مرحله 2: اجرا ================
FROM python:3.11-slim

WORKDIR /app

# کپی وابستگی‌ها از مرحله قبل
COPY --from=builder /root/.local /root/.local

# نصب وابستگی‌های سیستمی لازم برای اجرا
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# تنظیم PATH
ENV PATH=/root/.local/bin:$PATH

# کپی سورس کد
COPY . .

# ایجاد کاربر غیر روت
RUN useradd -m -u 1000 peakfinder && chown -R peakfinder:peakfinder /app
USER peakfinder

# expose پورت
EXPOSE 8000

# بررسی سلامت
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# دستور اجرا
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]