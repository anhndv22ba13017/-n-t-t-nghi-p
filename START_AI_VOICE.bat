@echo off
chcp 65001 >nul
echo =======================================================
echo     CHUONG TRINH KHOI DONG AI QWEN3-TTS OFFLINE
echo =======================================================

echo [1] Kiem tra xem ban da cai dac Python quoc dan chua...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [LOI] Khong tim thay Python! 
    echo May ban chua co bo suu tap hoac chua nap lenh vao Path.
    echo Vui long mo Microsoft Store len va tai "Python 3.11" roi moi mo lai file nay.
    pause
    exit
)

echo [2] Xoa moi truong o tap cu bi loi (Neu co)...
if exist .venv (
    rmdir /s /q .venv
)

echo [3] Khoi tao Moi truong Code moi cung...
python -m venv .venv
call .venv\Scripts\activate.bat

echo [4] Vao tui cai dat vu khi hang nang (PyTorch, Qwen-TTS)...
echo Vui long cho khoa 5-10 phut cho qua trinh nay (Phu thuoc mang)...
pip install --upgrade pip
pip install torch soundfile
pip install transformers accelerate
pip install qwen-tts modelscope

echo =======================================================
echo CAI DAT THANH CONG! TAI MO HINH VAO BO NHO NHO...
echo =======================================================

python test_my_ai_voice.py

echo.
echo =======================================================
echo XONG! FILE GIONG THU DA NAM TREN DESKTOP!
pause
