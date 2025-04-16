cd /d "%~dp0"
cd ..
if exist ".\app" rd /s /q ".\app"
mkdir ".\app"
xcopy .\main\app\*          .\app\ /c /e /h /r /y
xcopy .\main\resources\*    .\app\ /c /e /h /r /y
xcopy .\lib\*               .\app\ /c /e /h /r /y
tar -c -v --exclude=__pycache__ -f app.tar app
if exist ".\app" rd /s /q ".\app"
move ./app.tar /home/facefit/app.tar