[Setup]
AppName=LinguaEdit
AppVersion={#MyAppVersion}
AppPublisher=Daniel Nylander
AppPublisherURL=https://github.com/yeager/linguaedit
AppSupportURL=https://github.com/yeager/linguaedit/issues
DefaultDirName={autopf}\LinguaEdit
DefaultGroupName=LinguaEdit
OutputBaseFilename=LinguaEdit-{#MyAppVersion}-Setup
OutputDir=..\
Compression=lzma2
SolidCompression=yes
SetupIconFile=..\resources\icon.ico
UninstallDisplayIcon={app}\LinguaEdit.exe
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
LicenseFile=..\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "swedish"; MessagesFile: "compiler:Languages\Swedish.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "danish"; MessagesFile: "compiler:Languages\Danish.isl"
Name: "norwegian"; MessagesFile: "compiler:Languages\Norwegian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\LinguaEdit\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\LinguaEdit"; Filename: "{app}\LinguaEdit.exe"
Name: "{group}\{cm:UninstallProgram,LinguaEdit}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\LinguaEdit"; Filename: "{app}\LinguaEdit.exe"; Tasks: desktopicon

[Registry]
Root: HKCR; Subkey: ".po"; ValueType: string; ValueData: "LinguaEdit.File"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".pot"; ValueType: string; ValueData: "LinguaEdit.File"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".ts"; ValueType: string; ValueData: "LinguaEdit.File"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".xliff"; ValueType: string; ValueData: "LinguaEdit.File"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".xlf"; ValueType: string; ValueData: "LinguaEdit.File"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".arb"; ValueType: string; ValueData: "LinguaEdit.File"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "LinguaEdit.File"; ValueType: string; ValueData: "Translation File"; Flags: uninsdeletekey
Root: HKCR; Subkey: "LinguaEdit.File\DefaultIcon"; ValueType: string; ValueData: "{app}\LinguaEdit.exe,0"
Root: HKCR; Subkey: "LinguaEdit.File\shell\open\command"; ValueType: string; ValueData: """{app}\LinguaEdit.exe"" ""%1"""

[Run]
Filename: "{app}\LinguaEdit.exe"; Description: "{cm:LaunchProgram,LinguaEdit}"; Flags: nowait postinstall skipifsilent
