@echo off
powershell -Command "Set-NetIPInterface -InterfaceAlias 'Ethernet' -InterfaceMetric 10; Set-NetIPInterface -InterfaceAlias 'Wi-Fi' -InterfaceMetric 50"
pause