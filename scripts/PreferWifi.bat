@echo off
powershell -Command "Set-NetIPInterface -InterfaceAlias 'Wi-Fi' -InterfaceMetric 10; Set-NetIPInterface -InterfaceAlias 'Ethernet' -InterfaceMetric 50"
pause