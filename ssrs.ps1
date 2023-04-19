# Set up variables
$ReportServerUri = "http://corp-reports-01/ReportServer/ReportService2010.asmx?WSDL"
$User = "cgraham"
$Credentials = Get-Credential

# Connect to SSRS web service
$rs = New-WebServiceProxy -Uri $ReportServerUri -Credential $Credentials

# Get a list of subscriptions for the user
$Subscriptions = $rs.ListSubscriptions("/") #| Where-Object { $_.SubscriberName -eq $User }

foreach ($Subscription in $Subscriptions) {
    foreach ($parametervalue in $Subscription.DeliverySettings.ParameterValues){
        if ($parametervalue.Value -like "*$User*"){
            Write-Host $Subscription.Path
            Write-Host $Subscription.LastExecuted
            Write-Host "$($parametervalue.Value) In $($Subscription.Description) `n" 
        }
    }

}

# Loop through each subscription and remove it
# foreach ($Subscription in $Subscriptions) {
#     $rs.DeleteSubscription($Subscription.SubscriptionID)
# }

