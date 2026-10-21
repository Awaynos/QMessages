@echo off
cd /d "%~dp0"
set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"
"%PYTHON%" -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error
"%PYTHON%" -m PyInstaller --noconfirm --clean --windowed --onedir --name QMessages ^
  --icon icon.ico ^
  --version-file file_version_info.txt ^
  --add-data "icon.ico;." ^
  --add-data "icons;icons" ^
  --exclude-module PySide6.QtWebEngineCore ^
  --exclude-module PySide6.QtWebEngineWidgets ^
  --exclude-module PySide6.QtWebEngineQuick ^
  --exclude-module PySide6.QtWebChannel ^
  --exclude-module PySide6.QtPdf ^
  --exclude-module PySide6.QtPdfWidgets ^
  --exclude-module PySide6.Qt3DCore ^
  --exclude-module PySide6.Qt3DRender ^
  --exclude-module PySide6.QtMultimedia ^
  --exclude-module PySide6.QtMultimediaWidgets ^
  --exclude-module PySide6.QtQuick ^
  --exclude-module PySide6.QtQuickWidgets ^
  --exclude-module PySide6.QtQml ^
  --exclude-module PySide6.QtCharts ^
  --exclude-module PySide6.QtDataVisualization ^
  --exclude-module PySide6.QtSql ^
  --exclude-module PySide6.QtTest ^
  main.py
if errorlevel 1 goto :error
for %%f in (opengl32sw.dll Qt6Pdf.dll QtPdf.pyd QtPdfWidgets.pyd Qt6Quick.dll QtQuick.pyd QtQuickWidgets.pyd Qt6Qml.dll QtQml.pyd Qt6QmlModels.dll QtQmlModels.pyd Qt6QmlMeta.dll Qt6QmlWorkerScript.dll QtQmlWorkerScript.pyd Qt6Network.dll QtNetwork.pyd libcrypto-3.dll libssl-3.dll Qt6OpenGL.dll QtOpenGL.pyd QtOpenGLWidgets.pyd Qt6VirtualKeyboard.dll) do del /Q "dist\QMessages\_internal\PySide6\%%f" 2>nul
echo.
echo Done: dist\QMessages\QMessages.exe
pause
exit /b 0
:error
echo.
echo Build failed.
pause
exit /b 1
