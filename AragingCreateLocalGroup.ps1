$ARAgingGroupName = "ARAingCORP"

Write-Host "Starting script to create local group for $ARAgingGroupName"

# Verify that the exchange online group exists
$exchnageOnlineGroup = Get-DistributionGroupMember $ARAgingGroupName | Select-Object primarysmtpaddress -ErrorAction SilentlyContinue

if ($exchnageOnlineGroup -eq $null) {
    Write-Host "Exchange online group does not exist - exiting"
    break
} else {
    Write-Host "Exchange online group exists"
}

# See if the -local version of the group exists

$localGroupName = "$ARAgingGroupName-local"
$localGroup = Get-ADGroup -Identity "$ARAgingGroupName-local" -ErrorAction SilentlyContinue 

if ($localGroup -eq $null) {
    Write-Host "Local group does not exist"
} else {
    Write-Host "Local group exists already - exiting"
    break
}

# Create the local group distribution list with email and displayname set
write-host "Creating local group $ARAgingGroupName-local"

New-ADGroup -Name "$ARAgingGroupName-local" -GroupCategory Distribution -GroupScope Global -DisplayName "$ARAgingGroupName-local" -Path "OU=Groups,DC=MidwestHose,DC=com" -Description "Local group for $ARAgingGroupName" 

$localGroupEmail = "$localGroupName@midwesthose.com"

# Add the email address to the group
write-host "Setting email address for $localGroupName to $localGroupEmail"
Set-ADGroup $localGroupName -Replace @{mail="$localGroupEmail"}

# Add the members of the exchange online group to the local group
write-host "Adding members of $ARAgingGroupName to $localGroupName"
$exchnageOnlineGroup | ForEach-Object {
    write-host "Adding $($_.primarysmtpaddress)"
    # get the username from the email address
    $username = $_.primarysmtpaddress -replace "@midwesthose.com", ""
    Add-ADGroupMember -Identity "$ARAgingGroupName-local" -Members $username
}