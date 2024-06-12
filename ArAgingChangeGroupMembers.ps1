$AragingGroup = "ARAgingWIL"
$localGroupEmailName = "$AragingGroup-Local@midwesthose.com"
$localGroupName = "$AragingGroup-Local"

# protect myself from using this on a non araging group
if ($AragingGroup -notlike "ARAging*") {
    write-host "This script is only for araging groups"
    break
}

# if AragingGroup has local in the name, break
if ($AragingGroup -like "*local*") {
    write-host "This script is only for oneline araging groups"
    break
}

# Verify that the exchange online group exists
write-host "Verifying that $AragingGroup exists and its members"
Get-DistributionGroupMember $AragingGroup | Select-Object primarysmtpaddress -ErrorAction Stop | Format-Table

# Verify that the local group exists
write-host "Verifying that $localGroupName exists and its members"
Get-ADGroup -Identity $localGroupName -ErrorAction Stop | Select-Object SamAccountName  | Format-List



# remove any members but the lacal group from the exchange online group
Get-DistributionGroupMember $AragingGroup -ErrorAction Stop | Where-Object { $_.primarysmtpaddress -ne $localGroupEmailName } | ForEach-Object {
    write-host "Removing $($_.primarysmtpaddress)"
    Remove-DistributionGroupMember -Identity $AragingGroup -Member $_.primarysmtpaddress -Confirm:$false
}

# add the local group to the exchange online group
write-host "Adding $localGroupEmailName to $AragingGroup"
Add-DistributionGroupMember -Identity $AragingGroup -Member $localGroupEmailName

# Verify the members of the exchange online group
write-host "Verify that $AragingGroup members are correct"
Get-DistributionGroupMember $AragingGroup | Select-Object primarysmtpaddress -ErrorAction Stop
