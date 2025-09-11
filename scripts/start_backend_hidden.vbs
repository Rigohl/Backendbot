Set oShell = CreateObject("WScript.Shell")
oShell.CurrentDirectory = "C:\Users\DELL\Desktop\BackendBot"
oShell.Run chr(34) & "C:\Users\DELL\AppData\Local\Programs\Python\Python312\pythonw.exe" & chr(34) & " " & chr(34) & "C:\Users\DELL\Desktop\BackendBot\backend.py" & chr(34), 0, False
