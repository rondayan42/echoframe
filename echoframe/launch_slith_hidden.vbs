
Set WshShell = CreateObject("WScript.Shell")
WshShell.Environment("Process")("PYTHONPATH") = "C:\Users\moonl\OneDrive\Desktop\echoframe_final_complete"
WshShell.Environment("Process")("SDL_VIDEODRIVER") = "windib"
WshShell.Environment("Process")("PYTHONUNBUFFERED") = "1"
WshShell.CurrentDirectory = "C:\Users\moonl\OneDrive\Desktop\echoframe_final_complete"
WshShell.Run """C:\Users\moonl\OneDrive\Desktop\echoframe_final_complete\.venv\Scripts\pythonw.exe"" ""C:\Users\moonl\OneDrive\Desktop\echoframe_final_complete\slith_pet.py"" ""Ron""", 0, False
