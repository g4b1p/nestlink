' --- LANZADOR INVISIBLE FINAL ---

Dim WshShell, Result
Set WshShell = CreateObject("WScript.Shell")

' 1. Iniciar Servidor (Invisible y No-Bloqueante)
' La opción 0 (oculto) y False (no esperar) lo manda a segundo plano.
WshShell.Run "nestlink_servidor.exe", 0, False 

' 2. Esperar 5 segundos para que Flask se inicie
WScript.Sleep 5000 

' 3. Iniciar Cliente (Visible y Bloqueante)
' La opción 1 (ventana normal) es necesaria, aunque el EXE es -w (sin consola).
' El True final significa que el script se pausa aquí hasta que se cierre el cliente.
Result = WshShell.Run("nestlink_cliente.exe", 1, True)

' 4. El cliente se ha cerrado. Matar el servidor automáticamente.
' El comando taskkill se ejecuta de forma invisible (0, False).
WshShell.Run "taskkill /F /IM nestlink_servidor.exe /T", 0, False

Set WshShell = Nothing