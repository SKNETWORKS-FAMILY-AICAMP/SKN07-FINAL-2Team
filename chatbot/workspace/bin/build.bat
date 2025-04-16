cd /d "%~dp0"
cd ..
if exist ".\build" rd /s /q ".\build"
mkdir ".\build"
xcopy .\main\app\*          .\build\ /c /e /h /r /y
xcopy .\main\resources\*    .\build\ /c /e /h /r /y
xcopy .\lib\*               .\build\ /c /e /h /r /y
tar -c -v --exclude=__pycache__ -f app.tar build
if exist ".\build" rd /s /q ".\build"
move ./app.tar /home/facefit/app.tar