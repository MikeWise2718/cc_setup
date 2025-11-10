@echo off
echo Did you remember to bump the version? (y/n)
set /p response="Enter yes to continue: "
if /I "%response%"=="y" goto :continue
if /I "%response%"=="yes" goto :continue
echo Aborting install. Please bump the version first.
exit /b

:continue
uv tool install --force .
