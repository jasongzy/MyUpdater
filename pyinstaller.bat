@REM call %USERPROFILE%\anaconda3\Scripts\activate.bat
@REM pyinstaller.exe -D -w -i res/juice.ico --version-file version_file main.py
pyinstaller.exe --clean --noconfirm main.spec

@REM md dist\main\certifi
@REM copy %USERPROFILE%\anaconda3\Lib\site-packages\certifi\cacert.pem dist\main\certifi
copy %USERPROFILE%\anaconda3\Lib\site-packages\win32\pywintypes310.dll dist\main\
