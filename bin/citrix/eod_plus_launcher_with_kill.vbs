' Exceed on Demand / Jeppesen Launcher script for Citrix 

'''' Start of section intended to be edited by the customer ''''' 
  
EoDPath = "c:\program files\Hummingbird\Connectivity\Exceed onDemand Client 7\ExceedonDemand.exe" 
EoDHost = "h1cms95a.net.sas.dk" 
PythonPath = "C:\Start\Python27\pythonw.exe" 
PythonScriptLocation = "C:\Start" 
JavaWSPath = "C:\Windows\System32\javaws.exe" 
SessionServerURL = "https://h1cms98a.net.sas.dk:8443"
SessionServerURLSuffix = "?server=h1cms98a" 
  
'''' End of section intended to be edited by the customer ''''' 

' Append a non-repeating nonsense-suffix to the sessionserver URL, to work-around Java Web Start cache-validation bug
SessionServerURLSuffix = SessionServerURLSuffix & "&random=" & DateDiff("s", "06/02/1984 09:00:00", Now())

' Define complete expressions from the above given parameters 
EoDString = """" & EoDPath & """" & " -h " & EoDHost & " -c -;MultipleWindow.cfg -x -;passive.xs" 
WaitForEoDString = PythonPath & " " & PythonScriptLocation & "\waitforwindow.py -n ""X Window"" -t 180" 
LauncherString = JavaWSPath & " -localfile " & SessionServerURL & "/jws/Launcher.jnlp" & SessionServerURLSuffix 
WaitForLauncherString = PythonPath & " " & PythonScriptLocation & "\waitforwindow.py -n ""Launcher"" -t 180" 
KillExceedString = PythonPath & " " & PythonScriptLocation & "\killwindow.py --ln ""Launcher"" --ec ""HtxMainWindow"" --sleep 5 "
JavaLogging = "CMD /C C:\Start\JavaLogging.bat"

' Define function for executing our various execution strings 
Sub Run(ByVal sFile, ByVal bWait) 
    Dim shell 
    Set shell = CreateObject("WScript.Shell") 
    shell.Run sFile, 1, bWait 
    Set shell = Nothing 
End Sub 
  
' Start JavaLogging
Run JavaLogging, True

' Start EoD 
Run EoDString, False 
  
' Wait for EoD to start 
Run WaitForEoDString, True 
  
' Start Launcher 
Run LauncherString , False 

' Wait for Launcher to start 
Run WaitForLauncherString, True 

' Activate EoD killer
Run KillExceedString, True

