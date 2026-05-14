@echo off
chcp 65001 >nul
echo ====================================
echo 0. 配置临时代理
echo ====================================
set http_proxy=http://192.168.3.100:20172
set https_proxy=http://192.168.3.100:20172

echo ====================================
echo 1. 正在拉取最新代码 (git pull)...
echo ====================================
git pull
if %errorlevel% neq 0 (
    echo [错误] Git pull 失败，脚本已停止！
    pause
    exit /b
)

echo.
echo ====================================
echo 2. 正在执行 Python 脚本，请耐心等待...
echo ====================================
python .\youus.py
if %errorlevel% neq 0 (
    echo [错误] Python 脚本执行失败，脚本已停止！
    pause
    exit /b
)

echo.
echo ====================================
echo 3. 正在提交并推送代码...
echo ====================================
git add -A
git commit -m "update"
git push origin main
if %errorlevel% neq 0 (
    echo [错误] Git push 失败，请检查网络或冲突！
    pause
    exit /b
)

echo.
echo ====================================
echo 全部任务执行完毕！
echo ====================================
pause