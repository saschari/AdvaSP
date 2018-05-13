echo off
echo "Starting chrome headless"
start chrome --remote-debugging-port=9222 --enable-automation --headless
echo "Executing third party script"
python check_thirdParties.py
echo "Killing all running chrome task"
taskkill /F /IM chrome.exe
