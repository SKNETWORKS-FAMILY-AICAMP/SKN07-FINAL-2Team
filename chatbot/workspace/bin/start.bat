cd /d "%~dp0"
cd ..
uvicorn --env-file ./.env --app-dir ./main/app/ main:app