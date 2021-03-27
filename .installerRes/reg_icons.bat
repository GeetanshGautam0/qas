@echo off
title "Configuring Icons"
color f0
cd /d %~dp0
cd .. & cd ".icons"
cls
echo "Configuring icon for *.qa_export files; please wait..."
reg add "HKCR\.qa_export\DefaultIcon" /t REG_SZ /ve /d "%cd%\qa_export.ico" /f /reg:64

echo ""
echo "Configuring icon for *.qaQuiz files; please wait..."
reg add "HKCR\.qaQuiz\DefaultIcon" /t REG_SZ /ve /d "%cd%\qaQuiz.ico" /f /reg:64

echo ""
echo "Configuring icon for *.qaScore files; please wait..."
reg add "HKCR\.qaScore\DefaultIcon" /t REG_SZ /ve /d "%cd%\qaScore.ico" /f /reg:64

exit