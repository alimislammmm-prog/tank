@echo off
cls
echo ====================================
echo        GIT AUTOMATIC PUSH
echo ====================================
echo.

:: 1. Stage all changes FIRST (so push.bat itself is included)
git add .

:: 2. Prompt for commit message
set /p commit_msg="Enter commit message: "

:: If left empty, set default message
if "%commit_msg%"=="" set commit_msg=Auto-commit

:: 3. Commit changes
git commit -m "%commit_msg%"

:: 4. Sync with remote repository safely now that working tree is clean
echo.
echo Syncing with GitHub...
git pull --rebase alimislammmm-prog main

:: If pull had conflicts, abort gracefully
if errorlevel 1 (
    echo.
    echo [!] Rebase had conflicts. Aborting rebase...
    git rebase --abort
)

:: 5. Push to GitHub
echo.
echo Pushing to GitHub...
git push alimislammmm-prog main

echo.
echo ====================================
echo               DONE!
echo ====================================
pause