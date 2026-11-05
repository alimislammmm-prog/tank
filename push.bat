@echo off
cls
echo ====================================
echo        GIT AUTOMATIC PUSH
echo ====================================
echo.

:: 1. Stage all changes
git add .

:: 2. Prompt for commit message
set /p commit_msg="Enter commit message: "

:: If left empty, set default message
if "%commit_msg%"=="" set commit_msg=Auto-commit

:: 3. Commit changes
git commit -m "%commit_msg%"

:: 4. Sync with remote repository to avoid rejection errors
echo.
echo Syncing with GitHub...
git pull --rebase alimislammmm-prog main

:: 5. Push to GitHub
echo.
echo Pushing to GitHub...
git push alimislammmm-prog main

echo.
echo ====================================
echo               DONE!
echo ====================================
pause