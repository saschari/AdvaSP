echo off
echo "Starting chrome headless"
start chrome --remote-debugging-port=9222 --enable-automation --headless
echo "Executing python script"
python check_aip.py
echo "Killing all running chrome task"
taskkill /F /IM chrome.exe