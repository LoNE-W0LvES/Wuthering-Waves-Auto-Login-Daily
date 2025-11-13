; Wuthering Waves Lunite Auto-Login Installer
; Inno Setup Script

#define MyAppName "Wuthering Waves Lunite Auto-Login"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "LoNE WoLvES"
#define MyAppExeName "WUWATracker.exe"
#define MyAppURL "https://github.com/yourusername/wuwa-lunite-autologin"

[Setup]
; Basic Information
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=installer_info.txt
OutputDir=installer_output
OutputBaseFilename=WUWALuniteAutoLogin_Setup_v{#MyAppVersion}
SetupIconFile=icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

; Wizard Images
WizardImageFile=installer_banner.bmp
WizardSmallImageFile=installer_icon.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Launch at Windows startup"; GroupDescription: "Additional options:"; Flags: unchecked

[Files]
; Main Application Files
Source: "WUWATracker_v2.0.0\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// No custom code needed - app creates its own config files

[UninstallDelete]
Type: filesandordirs; Name: "{app}\ww_launcher_config.json"
Type: filesandordirs; Name: "{app}\ww_launcher_tracking.json"
Type: filesandordirs; Name: "{app}\debug_screenshot.png"
Type: filesandordirs; Name: "{app}\*.log"