@echo off
echo ==============================
echo 法律AI - 启动脚本
echo ==============================

echo.
echo [1/2] 启动后端服务...
cd backend
start cmd /k "..\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [2/2] 打开应用页面...
timeout /t 3 >nul
start http://127.0.0.1:8000/

echo.
echo ==============================
echo 启动完成！
echo 已使用项目虚拟环境 .venv
echo 后端地址: http://127.0.0.1:8000
echo 应用入口: http://127.0.0.1:8000/
echo ==============================
pause
