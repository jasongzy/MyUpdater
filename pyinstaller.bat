@REM call %USERPROFILE%\anaconda3\Scripts\activate.bat

@REM pyinstaller.exe -D --hide_console hide-early -i res/juice.ico --version-file version_file main.py

@REM pyi-makespec ...
pyinstaller.exe --clean --noconfirm main.spec
rd/s/q build

@REM md dist\main\certifi
@REM copy %USERPROFILE%\anaconda3\Lib\site-packages\certifi\cacert.pem dist\main\certifi
@REM copy %USERPROFILE%\anaconda3\Lib\site-packages\win32\pywintypes310.dll dist\main\
