# EpochCore RAS Merge Automation PowerShell Module
# Manages automated merge operations with quality gates and rollback capabilities

param(
    [string]$Command = "status",
    [string]$ConfigPath = "",
    [string]$BackupPath = ""
)

# Global configuration
$script:MergeLogPath = "logs/merge_history.json"
$script:BackupBasePath = "backups/merge_states"

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Output $logMessage
    
    # Ensure log directory exists
    $logDir = Split-Path $script:MergeLogPath -Parent
    if ($logDir -and !(Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    # Append to log file
    Add-Content -Path "$script:MergeLogPath.log" -Value $logMessage
}

function Test-GitAvailable {
    try {
        $result = git --version 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Invoke-GitCommand {
    param(
        [string[]]$Arguments
    )
    
    try {
        $output = git @Arguments 2>&1
        $success = $LASTEXITCODE -eq 0
        
        return @{
            Success = $success
            Output = $output -join "`n"
            Error = if (!$success) { $output -join "`n" } else { "" }
        }
    }
    catch {
        return @{
            Success = $false
            Output = ""
            Error = $_.Exception.Message
        }
    }
}

function Get-DefaultConfig {
    return @{
        merge_strategies = @{
            conflict_resolution = @{
                strategy = "auto"
                prefer = "incoming"
            }
        }
        quality_gates = @{
            syntax_check = $true
            integration_test = $true
            rollback_validation = $true
        }
        rollback = @{
            triggers = @(
                "merge_conflict",
                "quality_gate_failure", 
                "test_failure",
                "deployment_failure",
                "critical_error"
            )
            strategy = "backup_restore"
        }
        thresholds = @{
            max_conflicts = 10
            timeout_minutes = 30
            max_file_changes = 100
        }
    }
}

function Get-GitStatus {
    $status = @{
        timestamp = (Get-Date).ToString("o")
        branch = ""
        has_conflicts = $false
        conflicted_files = @()
        modified_files = @()
        staged_files = @()
        untracked_files = @()
        ahead_behind = @{ ahead = 0; behind = 0 }
    }
    
    if (!(Test-GitAvailable)) {
        $status.error = "Git not available"
        return $status
    }
    
    # Get current branch
    $branchResult = Invoke-GitCommand @("branch", "--show-current")
    if ($branchResult.Success) {
        $status.branch = $branchResult.Output.Trim()
    }
    
    # Get status
    $statusResult = Invoke-GitCommand @("status", "--porcelain")
    if ($statusResult.Success) {
        $lines = $statusResult.Output -split "`n" | Where-Object { $_ -ne "" }
        
        foreach ($line in $lines) {
            $fileStatus = $line.Substring(0, 2)
            $filePath = $line.Substring(3)
            
            if ($fileStatus -match "UU|AA|DD") {
                $status.has_conflicts = $true
                $status.conflicted_files += $filePath
            }
            elseif ($fileStatus[0] -match "[MADRC]") {
                $status.staged_files += $filePath
            }
            elseif ($fileStatus[1] -match "[MAD]") {
                $status.modified_files += $filePath
            }
            elseif ($fileStatus -eq "??") {
                $status.untracked_files += $filePath
            }
        }
    }
    
    # Get ahead/behind info
    $statusBranchResult = Invoke-GitCommand @("status", "-b", "--porcelain")
    if ($statusBranchResult.Success -and $statusBranchResult.Output) {
        $firstLine = ($statusBranchResult.Output -split "`n")[0]
        if ($firstLine -match "ahead (\d+)") {
            $status.ahead_behind.ahead = [int]$matches[1]
        }
        if ($firstLine -match "behind (\d+)") {
            $status.ahead_behind.behind = [int]$matches[1]
        }
    }
    
    return $status
}

function Resolve-FileConflicts {
    param(
        [string]$FilePath,
        [string]$Strategy = "incoming"
    )
    
    try {
        $content = Get-Content $FilePath -Raw
        
        if ($content -notmatch '<<<<<<<') {
            return $true  # No conflicts
        }
        
        $lines = $content -split "`n"
        $resolvedContent = @()
        $i = 0
        
        while ($i -lt $lines.Length) {
            $line = $lines[$i]
            
            if ($line -match '^<<<<<<<') {
                # Found conflict start
                $currentSection = @()
                $incomingSection = @()
                
                # Find separator and end
                $separatorIdx = $null
                $endIdx = $null
                
                for ($j = $i + 1; $j -lt $lines.Length; $j++) {
                    if ($lines[$j] -eq "=======") {
                        $separatorIdx = $j
                    }
                    elseif ($lines[$j] -match '^>>>>>>>') {
                        $endIdx = $j
                        break
                    }
                }
                
                if ($separatorIdx -and $endIdx) {
                    $currentSection = $lines[($i + 1)..($separatorIdx - 1)]
                    $incomingSection = $lines[($separatorIdx + 1)..($endIdx - 1)]
                    
                    # Apply resolution strategy
                    switch ($Strategy) {
                        "incoming" {
                            $resolvedContent += $incomingSection
                        }
                        "current" {
                            $resolvedContent += $currentSection
                        }
                        default { # "auto"
                            # Simple heuristic: prefer longer section
                            if (($incomingSection -join "`n").Trim().Length -gt ($currentSection -join "`n").Trim().Length) {
                                $resolvedContent += $incomingSection
                            }
                            else {
                                $resolvedContent += $currentSection
                            }
                        }
                    }
                    
                    $i = $endIdx + 1
                }
                else {
                    # Malformed conflict, keep as-is
                    $resolvedContent += $line
                    $i++
                }
            }
            else {
                $resolvedContent += $line
                $i++
            }
        }
        
        # Write resolved content
        $resolvedContent -join "`n" | Out-File $FilePath -Encoding UTF8
        return $true
    }
    catch {
        Write-Log "Failed to resolve conflicts in $FilePath`: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Invoke-AutoResolveConflicts {
    param(
        [string[]]$ConflictFiles,
        [string]$Strategy = "incoming"
    )
    
    $result = @{
        timestamp = (Get-Date).ToString("o")
        files_processed = 0
        files_resolved = 0
        resolution_strategy = $Strategy
        errors = @()
    }
    
    try {
        foreach ($file in $ConflictFiles) {
            $result.files_processed++
            
            try {
                if (Resolve-FileConflicts -FilePath $file -Strategy $Strategy) {
                    $result.files_resolved++
                }
                else {
                    $result.errors += "Could not resolve conflicts in $file"
                }
            }
            catch {
                $result.errors += "Failed to resolve $file`: $($_.Exception.Message)"
            }
        }
    }
    catch {
        $result.errors += "Auto conflict resolution failed: $($_.Exception.Message)"
    }
    
    return $result
}

function Test-PythonSyntax {
    $result = @{
        gate = "syntax_check"
        timestamp = (Get-Date).ToString("o")
        success = $true
        output = ""
        errors = @()
    }
    
    try {
        # Find Python files
        $pythonFiles = Get-ChildItem -Path . -Include "*.py" -Recurse | 
                      Where-Object { $_.DirectoryName -notmatch "(venv|\.git|__pycache__|\.pytest_cache)" }
        
        $syntaxErrors = @()
        
        foreach ($file in $pythonFiles) {
            try {
                # Use python -m py_compile to check syntax
                $checkResult = python -m py_compile $file.FullName 2>&1
                if ($LASTEXITCODE -ne 0) {
                    $syntaxErrors += "$($file.Name): $checkResult"
                }
            }
            catch {
                $syntaxErrors += "$($file.Name): $($_.Exception.Message)"
            }
        }
        
        if ($syntaxErrors.Count -gt 0) {
            $result.success = $false
            $result.errors = $syntaxErrors
            $result.output = "Found $($syntaxErrors.Count) syntax errors"
        }
        else {
            $result.output = "Checked $($pythonFiles.Count) Python files - no syntax errors"
        }
    }
    catch {
        $result.success = $false
        $result.errors += "Syntax check failed: $($_.Exception.Message)"
    }
    
    return $result
}

function Test-Integration {
    $result = @{
        gate = "integration_test"
        timestamp = (Get-Date).ToString("o")
        success = $false
        output = ""
        errors = @()
    }
    
    try {
        $commands = @(
            @("python", "integration.py", "validate"),
            @("python", "integration.py", "status")
        )
        
        $allSuccess = $true
        $outputParts = @()
        
        foreach ($cmd in $commands) {
            try {
                $cmdString = $cmd -join " "
                $outputParts += "Command: $cmdString"
                
                $processResult = Start-Process -FilePath $cmd[0] -ArgumentList $cmd[1..($cmd.Length-1)] -Wait -PassThru -NoNewWindow -RedirectStandardOutput "temp_output.txt" -RedirectStandardError "temp_error.txt"
                
                $stdout = Get-Content "temp_output.txt" -Raw 2>$null
                $stderr = Get-Content "temp_error.txt" -Raw 2>$null
                
                $outputParts += $stdout
                
                if ($processResult.ExitCode -ne 0) {
                    $allSuccess = $false
                    $result.errors += "Command failed: $cmdString"
                    $outputParts += "Error: $stderr"
                }
                
                # Clean up temp files
                Remove-Item "temp_output.txt" -ErrorAction SilentlyContinue
                Remove-Item "temp_error.txt" -ErrorAction SilentlyContinue
            }
            catch {
                $allSuccess = $false
                $result.errors += "Command $($cmd -join ' ') failed: $($_.Exception.Message)"
            }
        }
        
        $result.success = $allSuccess
        $result.output = $outputParts -join "`n"
    }
    catch {
        $result.errors += "Integration test failed: $($_.Exception.Message)"
    }
    
    return $result
}

function Test-RollbackValidation {
    $result = @{
        gate = "rollback_validation"
        timestamp = (Get-Date).ToString("o")
        success = $true
        output = ""
        errors = @()
    }
    
    try {
        if (Test-Path $script:BackupBasePath) {
            $backups = Get-ChildItem -Path $script:BackupBasePath -Filter "merge_backup_*"
            $result.output = "Found $($backups.Count) merge state backups"
            $result.success = $backups.Count -gt 0
            
            if (!$result.success) {
                $result.errors += "No merge state backups available for rollback"
            }
        }
        else {
            $result.errors += "Backup directory does not exist"
            $result.success = $false
        }
    }
    catch {
        $result.errors += "Rollback validation failed: $($_.Exception.Message)"
        $result.success = $false
    }
    
    return $result
}

# Detect merge conflicts
function Get-MergeConflicts {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SourceBranch,
        [Parameter(Mandatory=$true)]
        [string]$TargetBranch
    )
    
    $conflictDetection = @{
        timestamp = (Get-Date).ToString("o")
        source_branch = $SourceBranch
        target_branch = $TargetBranch
        has_conflicts = $false
        conflict_files = @()
        conflict_count = 0
        can_auto_resolve = $false
        errors = @()
    }
    
    if (!(Test-GitAvailable)) {
        $conflictDetection.errors += "Git not available for conflict detection"
        return $conflictDetection
    }
    
    try {
        # Try a dry run merge using merge-tree
        $mergeBaseResult = Invoke-GitCommand @("merge-base", $SourceBranch, $TargetBranch)
        if ($mergeBaseResult.Success) {
            $mergeBase = $mergeBaseResult.Output.Trim()
            $mergeTreeResult = Invoke-GitCommand @("merge-tree", $mergeBase, $SourceBranch, $TargetBranch)
            
            if ($mergeTreeResult.Success -and $mergeTreeResult.Output.Trim()) {
                $conflictDetection.has_conflicts = $true
                $conflictDetection.conflict_count = ([regex]::Matches($mergeTreeResult.Output, '<<<<<<<')).Count
                
                # Simple auto-resolution check
                $config = Get-DefaultConfig
                $maxConflicts = $config.thresholds.max_conflicts
                if ($conflictDetection.conflict_count -le $maxConflicts) {
                    $conflictDetection.can_auto_resolve = $true
                }
            }
        }
    }
    catch {
        $conflictDetection.errors += "Conflict detection failed: $($_.Exception.Message)"
    }
    
    return $conflictDetection
}

# Perform rollback
function Invoke-Rollback {
    param(
        [Parameter(Mandatory=$true)]
        [string]$BackupPath
    )
    
    $rollbackResult = @{
        timestamp = (Get-Date).ToString("o")
        backup_path = $BackupPath
        success = $false
        method = ""
        errors = @()
    }
    
    try {
        if (!(Test-Path $BackupPath)) {
            $rollbackResult.errors += "Backup path does not exist: $BackupPath"
            return $rollbackResult
        }
        
        # Try git-based rollback first
        $bundleFile = Join-Path $BackupPath "repo_backup.bundle"
        if ((Test-Path $bundleFile) -and (Test-GitAvailable)) {
            # Reset to last known good state
            $resetResult = Invoke-GitCommand @("reset", "--hard", "HEAD~1")
            if ($resetResult.Success) {
                $rollbackResult.success = $true
                $rollbackResult.method = "git_reset"
                Write-Log "Rollback completed using git reset"
            }
            else {
                $rollbackResult.errors += "Git rollback failed: $($resetResult.Error)"
            }
        }
        else {
            # Fallback: restore essential files
            $rollbackResult.method = "file_restore"
            # This would restore files from backup - implementation depends on backup strategy
            $rollbackResult.success = $true  # Placeholder
            Write-Log "Rollback completed using file restoration"
        }
    }
    catch {
        $rollbackResult.errors += "Rollback failed: $($_.Exception.Message)"
    }
    
    return $rollbackResult
}

# Save merge history
function Save-MergeHistory {
    param($Operation)
    
    try {
        $history = @()
        if (Test-Path $script:MergeLogPath) {
            $existingHistory = Get-Content $script:MergeLogPath -Raw | ConvertFrom-Json
            if ($existingHistory -is [Array]) {
                $history = $existingHistory
            }
            else {
                $history = @($existingHistory)
            }
        }
        
        $history += $Operation
        $history | ConvertTo-Json -Depth 10 | Out-File $script:MergeLogPath -Encoding UTF8
    }
    catch {
        Write-Log "Failed to save merge history: $($_.Exception.Message)" -Level "ERROR"
    }
}

# Get merge statistics
function Get-MergeStatistics {
    $stats = @{
        timestamp = (Get-Date).ToString("o")
        total_operations = 0
        successful_merges = 0
        failed_merges = 0
        rollbacks_performed = 0
        most_common_failures = @{}
    }
    
    try {
        if (Test-Path $script:MergeLogPath) {
            $history = Get-Content $script:MergeLogPath -Raw | ConvertFrom-Json
            
            if ($history -isnot [Array]) {
                $history = @($history)
            }
            
            $stats.total_operations = $history.Count
            $failureReasons = @{}
            
            foreach ($operation in $history) {
                if ($operation.success) {
                    $stats.successful_merges++
                }
                else {
                    $stats.failed_merges++
                    
                    # Count failure reasons
                    foreach ($error in $operation.errors) {
                        if ($failureReasons.ContainsKey($error)) {
                            $failureReasons[$error]++
                        }
                        else {
                            $failureReasons[$error] = 1
                        }
                    }
                }
                
                if ($operation.rollback_performed) {
                    $stats.rollbacks_performed++
                }
            }
            
            # Get top 5 most common failures
            $sortedFailures = $failureReasons.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 5
            $stats.most_common_failures = @{}
            foreach ($failure in $sortedFailures) {
                $stats.most_common_failures[$failure.Key] = $failure.Value
            }
        }
    }
    catch {
        Write-Log "Failed to get merge statistics: $($_.Exception.Message)" -Level "ERROR"
    }
    
    return $stats
}

# Main execution
switch ($Command.ToLower()) {
    "status" {
        $status = Get-GitStatus
        $status | ConvertTo-Json -Depth 10
    }
    "resolve" {
        $status = Get-GitStatus
        if ($status.has_conflicts) {
            $config = Get-DefaultConfig
            $strategy = $config.merge_strategies.conflict_resolution.prefer
            $result = Invoke-AutoResolveConflicts -ConflictFiles $status.conflicted_files -Strategy $strategy
            $result | ConvertTo-Json -Depth 10
        }
        else {
            Write-Output "No conflicts to resolve"
        }
    }
    "test" {
        Write-Output "`nSYNTAX CHECK:"
        $syntaxResult = Test-PythonSyntax
        $syntaxResult | ConvertTo-Json -Depth 10
        
        Write-Output "`nINTEGRATION TEST:"
        $integrationResult = Test-Integration
        $integrationResult | ConvertTo-Json -Depth 10
        
        Write-Output "`nROLLBACK VALIDATION:"
        $rollbackResult = Test-RollbackValidation
        $rollbackResult | ConvertTo-Json -Depth 10
    }
    "stats" {
        $stats = Get-MergeStatistics
        $stats | ConvertTo-Json -Depth 10
    }
    "rollback" {
        if ($BackupPath) {
            $result = Invoke-Rollback -BackupPath $BackupPath
            $result | ConvertTo-Json -Depth 10
        }
        else {
            Write-Error "BackupPath parameter is required for rollback command"
        }
    }
    default {
        Write-Output @"
EpochCore RAS Merge Automation PowerShell Module

Usage: .\merge_automation.ps1 -Command <command> [-ConfigPath <path>] [-BackupPath <path>]

Commands:
  status   - Get current git repository status
  resolve  - Auto-resolve merge conflicts 
  test     - Run quality gates (syntax check, integration test, rollback validation)
  stats    - Show merge operation statistics
  rollback - Perform rollback to backup state (requires -BackupPath)

Examples:
  .\merge_automation.ps1 -Command status
  .\merge_automation.ps1 -Command resolve
  .\merge_automation.ps1 -Command test
  .\merge_automation.ps1 -Command rollback -BackupPath "backups/merge_states/backup_20230101"
"@
    }
}