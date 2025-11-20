@echo off
TITLE NestLink Server & Client Launcher

echo.
echo ==================================================
echo.
echo 1. Iniciando Servidor NestLink (Mantener esta ventana abierta)
echo.

:: Inicia el servidor en una nueva ventana
START "NestLink Server" "nestlink_servidor.exe"

:: Esperar 5 segundos para que el servidor se inicialice
TIMEOUT /T 5 /NOBREAK > NUL

echo --------------------------------------------------
echo.
echo 2. Iniciando Cliente NestLink
echo.
echo ==================================================

:: Ejecutamos el cliente. Eliminamos 'call' para simplificar.
nestlink_cliente.exe

echo.
echo --------------------------------------------------
echo El cliente se ha cerrado. Revise los errores anteriores.
PAUSE
:END