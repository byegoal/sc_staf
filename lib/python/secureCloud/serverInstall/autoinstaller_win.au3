#include <file.au3>
if $cmdLine[0]>0 then
	$inifile = $cmdLine[1]
Else
	$inifile = "scopinstall.ini"
endif
;---------load config-----------
$Servername = IniRead($inifile,"install","Servername", "ERROR")
$Certlocation = IniRead($inifile,"install","Certlocation", "ERROR")
$Certpassphrase = IniRead($inifile,"install","Certpassphrase", "ERROR")
$Serviceaccount = IniRead($inifile,"install","Serviceaccount", "ERROR")
$Serviceaccountpw = IniRead($inifile,"install","Serviceaccountpw", "ERROR")
$Sqlname = IniRead($inifile,"install","Sqlname", "ERROR")
$Sqlserver = IniRead($inifile,"install","Sqlserver", "ERROR")
$Sqlaccount = IniRead($inifile,"install","Sqlaccount", "ERROR")
$Sqlaccountpw = IniRead($inifile,"install","Sqlaccountpw", "ERROR")
$Sqlkeyfile = IniRead($inifile,"install","Sqlkeyfile", "ERROR")
$Sqlkeyfilepw = IniRead($inifile,"install","Sqlkeyfilepw", "ERROR")
$Reportingserver = IniRead($inifile,"install","Reportingserver", "ERROR")
$Company = IniRead($inifile,"install","Company", "ERROR")
$Fname = IniRead($inifile,"install","Fname", "ERROR")
$Lname = IniRead($inifile,"install","Lname", "ERROR")
$Emailaddress = IniRead($inifile,"install","Emailaddress", "ERROR")
$Userpw = IniRead($inifile,"install","Userpw", "ERROR")
$Excutelocation = IniRead($inifile,"install","Excutelocation", "ERROR")
$chooseip = IniRead($inifile,"install","chooseip", "ERROR")
$ipaddress = IniRead($inifile,"install","ipaddress", "ERROR")
$choosewebport = IniRead($inifile,"install","choosewebport", "ERROR")
$webconsolesslport = IniRead($inifile,"install","webconsolesslport", "ERROR")
$cmcsslport = IniRead($inifile,"install","cmcsslport", "ERROR")
$webserviceport = IniRead($inifile,"install","webserviceport", "ERROR")
$readytoinstall = IniRead($inifile,"install","readytoinstall", "ERROR")
$sleeptime = IniRead($inifile,"install","sleeptime", "ERROR")

;---------setting installer related variable-----------
$win_title = "Trend Micro SecureCloud Management Server Setup"
$win_title2 = "Trend Micro SecureCloud Management Server"
;---------Start Installer-----------
run($Excutelocation)
;--------- Warning dialog for installer -----------
WinWait($win_title,"The Setup Wizard will install Trend Micro SecureCloud Management Server on your computer")
sleep($sleeptime)
WinActivate($win_title,"The Setup Wizard will install Trend Micro SecureCloud Management Server on your computer")
WinWaitActive($win_title,"The Setup Wizard will install Trend Micro SecureCloud Management Server on your computer")
Send("!n")

;--------- License aggreement page -----------
WinWaitActive($win_title,"Please read the following license agreement carefully")
Send("!a")
Send("!n")

;--------- choose setup type page -----------
WinWaitActive($win_title,"Choose the setup type that best suits your needs")
Send("!t")

;--------- web site configuration page -----------
WinWaitActive($win_title,"Website Configuration")
ControlCommand($win_title,"","RichEdit20W1","EditPaste",$Servername)
if $chooseip=1 Then
ControlCommand($win_title,"","ComboBox1", "SelectString", $ipaddress)
EndIf
ControlCommand($win_title,"","RichEdit20W2","EditPaste",$Certlocation)
ControlCommand($win_title,"","Edit1","EditPaste",$Certpassphrase)
if $choosewebport=1 Then
ControlFocus($win_title,"","Edit2")
Send("{DEL 1}")
ControlCommand($win_title,"","Edit2","EditPaste",$webconsolesslport)
ControlFocus($win_title,"","Edit3")
Send("{DEL 1}")
ControlCommand($win_title,"","Edit3","EditPaste",$cmcsslport)
ControlFocus($win_title,"","Edit4")
Send("{DEL 1}")
ControlCommand($win_title,"","Edit4","EditPaste",$webserviceport)
EndIf
ControlFocus($win_title,"","RichEdit20W1")
Send("{TAB 1}") 
Send("{TAB 1}") 
Send("{TAB 1}") 
Send("{TAB 1}") 
sleep($sleeptime)
Send("!n")

;--------- Server account page -----------
WinWaitActive($win_title,"Service Account")
ControlCommand($win_title,"","RichEdit20W2","EditPaste",$Serviceaccount)
ControlCommand($win_title,"","Edit1","EditPaste",$Serviceaccountpw)
ControlCommand($win_title,"","Edit2","EditPaste",$Serviceaccountpw)
ControlFocus($win_title,"","RichEdit20W2")
Send("{TAB 1}") 
Send("{TAB 1}") 
Send("{TAB 1}") 
sleep($sleeptime)
Send("!n")

;--------- Database Configuration page -----------
WinWaitActive($win_title,"Database Configuration")
ControlCommand($win_title,"","RichEdit20W1","EditPaste",$Sqlname)
ControlCommand($win_title,"","RichEdit20W2","EditPaste",$Sqlserver)
ControlCommand($win_title,"","RichEdit20W4","EditPaste",$Sqlaccount)
ControlFocus($win_title,"","Edit1")
ControlCommand($win_title,"","Edit1","EditPaste",$Sqlaccountpw)
ControlCommand($win_title,"","RichEdit20W5","EditPaste",$Sqlkeyfile)
ControlCommand($win_title,"","Edit2","EditPaste",$Sqlkeyfilepw)
ControlFocus($win_title,"","RichEdit20W4")
Send("{TAB 1}")
Send("{TAB 1}") 
Send("{TAB 1}")
Send("{TAB 1}") 
Send("{TAB 1}") 
Send("{TAB 1}") 
Send("{TAB 1}") 
Send("{TAB 1}")
Send("{TAB 1}") 
Send("{TAB 1}") 
Send("{TAB 1}") 
Send("{TAB 1}") 
sleep($sleeptime)
Send("!n")

;--------- Report Configuration page -----------
WinWaitActive($win_title,"Reporting Configuration")
ControlCommand($win_title,"","RichEdit20W1","EditPaste",$Reportingserver)
sleep($sleeptime)
$RS_connect = 0
While $RS_connect = 0
ControlClick($win_title, "", "Button1")
sleep("5000")
if WinExists ($win_title,"Unable to connect to the specified reporting service. Please check your settings and if the reporting service is running, then try again.") then 
ControlClick($win_title, "", "Button1")
elseif WinExists ($win_title,"Reporting Service connection successful.") then
$RS_connect = 1
ControlClick($win_title, "", "Button1")
endif
Wend
Send("!n")

;---------  System Administrator Configuration page -----------
WinWaitActive($win_title,"System Administrator Configuration")
ControlCommand($win_title,"","RichEdit20W1","EditPaste",$Company)
ControlCommand($win_title,"","RichEdit20W2","EditPaste",$Fname)
ControlCommand($win_title,"","RichEdit20W3","EditPaste",$Lname)
ControlCommand($win_title,"","RichEdit20W4","EditPaste",$Emailaddress)
ControlCommand($win_title,"","Edit1","EditPaste",$Userpw)
ControlCommand($win_title,"","Edit2","EditPaste",$Userpw)
ControlFocus($win_title,"","RichEdit20W2")
Send("{TAB 1}")
Send("{TAB 1}")
Send("{TAB 1}") 
Send("{TAB 1}") 
Send("{TAB 1}") 
Send("{TAB 1}") 
sleep($sleeptime)
Send("!n")

;---------  Installation Summary page -----------
WinWaitActive($win_title,"Ready to install Trend Micro SecureCloud Management Server")
if $readytoinstall = 1 Then
sleep($sleeptime)
Send("!i")
EndIf

;---------  Installation finish page -----------
;WinWait($win_title,"Completed the Trend Micro SecureCloud Management Server Setup Wizard")
;WinActivate($win_title,"Completed the Trend Micro SecureCloud Management Server Setup Wizard")
;sleep($sleeptime)
;Send("!f")

WinWait($win_title, "Click the Finish button to exit the Setup Wizard")
;ControlClick($win_title, "Click the Finish button to exit the Setup Wizard", "Button6") ;uncheck "view README file"
ControlClick($win_title, "Click the Finish button to exit the Setup Wizard", "Button1");after build 1034 2008 doesn't need to reboot.  
;after build 1035 will ask user to reset iis
WinWait($win_title, "restart IIS Services now",60)
ControlClick($win_title, "restart IIS Services now", "Button1")
    
