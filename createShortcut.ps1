$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("$Home\Desktop\Run Zara.lnk")

# Dynamically set the target path to "Run.bat" in the current script's directory.
$Shortcut.TargetPath = Join-Path -Path $PSScriptRoot -ChildPath "Run.bat"

# Dynamically set the icon location to "app\Portrait\Zara.ico" relative to the current script's directory.
$Shortcut.IconLocation = Join-Path -Path $PSScriptRoot -ChildPath "app\Portrait\icon.ico"

$Shortcut.Save()
