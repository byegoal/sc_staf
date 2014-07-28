@ECHO OFF
:: set ini file path according to the location of run.bat
SET INI_PATH=%0
if "%INI_PATH:~-3%"=="run" (
 SET INI_PATH=%INI_PATH:~,-3%
) ELSE (
 SET INI_PATH=%INI_PATH:~,-7%
)
IF "%TMSTAF_HOME%" == "" (
  SET TMSTAF_HOME=C:\staf\lib\python\tmstaf
)
@ECHO ON
python %TMSTAF_HOME%\tmstafMain.py -c %INI_PATH%tmstaf.ini %*