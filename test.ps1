
search-mailboxAuditLog remittances -ShowDetails -StartDate 12/01/2023 -EndDate 12/16/2023   | Where-Object -Property SourceItemSubjectsList -EQ "Payment Advice Note from 12/13/2023" `
| Select-Object -Property SourceItemSubjectsList, Operation, OperationResult, FolderPathName, LogonUserDisplayName, LastAccessed | Format-Table

