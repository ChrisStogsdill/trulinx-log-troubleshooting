# This script will keep calling the AutoPrintFolderMonitor python script. 
# Trying to run the python script by itself will stop working overnight for some reason
# It is now set to stop itself after about 5 hours, this script will keep calling it when it stops itself.
while ($true) {
    python .\AutoPrintFolderMonitor.py

    # cleanup the logs folder. 
    # delete files older than 7 days in logs folder
    Get-ChildItem –Path ".\logs" -Recurse | Where-Object {($_.LastWriteTime -gt (Get-Date).AddDays(-7))} | Remove-Item

}