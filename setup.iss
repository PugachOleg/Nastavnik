[Setup]
AppName=Семейный Наставник
AppVersion=1.0
AppPublisher=Олег Юрьевич
DefaultDirName={autopf}\FamilyMentor
DefaultGroupName=Семейный Наставник
OutputDir=Output
OutputBaseFilename=FamilyMentor_Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Files]
; Копируем все файлы проекта (включая assets)
Source: "*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
; Установщик Ollama (если он есть в папке проекта) – будет скопирован во временную папку и удалён после установки
Source: "OllamaSetup.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
; Ярлык в меню Пуск с иконкой status.ico (иконка должна лежать в папке assets проекта)
Name: "{group}\Семейный Наставник"; Filename: "{app}\run_app.bat"; IconFilename: "{app}\assets\status.ico"
; Ярлык на рабочем столе с той же иконкой
Name: "{commondesktop}\Семейный Наставник"; Filename: "{app}\run_app.bat"; IconFilename: "{app}\assets\status.ico"

[Run]
; Тихая установка Ollama (если файл OllamaSetup.exe был скопирован во временную папку)
Filename: "{tmp}\OllamaSetup.exe"; Parameters: "/VERYSILENT"; StatusMsg: "Установка Ollama..."; Flags: runhidden waituntilterminated
; Никакого автоматического запуска run_app.bat – пользователь запустит ярлык сам.