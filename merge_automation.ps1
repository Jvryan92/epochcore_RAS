# Merge Automation PowerShell - EpochCore RAS
# PowerShell-based robust merge logic for integrating changes into main branch
# Generated: 2025-09-03

param(
    [string]$SourceBranch = "",
    [string]$TargetBranch = "main",
    [string]$Strategy = "merge",
    [string]$ConfigPath = "merge_config.yaml",
    [string]$RepoPath = ".",
    [switch]$Status,
    [switch]$Validate,
    [switch]$Force,
    [switch]$Verbose
)

# Set error handling
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Import required modules
try {
    Import-Module powershell-yaml -ErrorAction SilentlyContinue
    $YamlAvailable = $true
}
catch {
    $YamlAvailable = $false
    Write-Warning "powershell-yaml module not available. Using JSON fallback."
}

# Global configuration
$Script:Config = @{
    merge_settings = @{
        auto_merge_enabled = $true
        conflict_resolution_strategy = "smart"
        backup_before_merge = $true
        run_tests_before_merge = $true
        create_merge_pr = $true
    }
    branch_settings = @{
        main_branch = "main"
        development_branch = "develop"
        feature_prefix = "feature/"
        hotfix_prefix = "hotfix/"
        protected_branches = @("main", "master", "production")
    }
    conflict_resolution = @{
        auto_resolve_simple = $true
        prefer_incoming_for = @("*.md", "*.txt", "*.json")
        prefer_current_for = @("*.py", "*.yaml", "*.yml")
        manual_review_required = @("integration.py", "requirements.txt")
        merge_tools = @("git", "diff3")
    }
    quality_gates = @{
        run_linting = $true
        run_unit_tests = $true
        run_integration_tests = $true
        security_scan = $true
        performance_check = $false
    }
    notification_settings = @{
        notify_on_success = $true
        notify_on_failure = $true
        notify_on_conflicts = $true
        webhook_url = $null
    }
}

# Logging function
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    Write-Host $logMessage
    
    # Write to log file
    $logFile = Join-Path $RepoPath "logs\merge_operations_ps.log"
    $logMessage | Add-Content -Path $logFile -ErrorAction SilentlyContinue
}

# Configuration loading
function Load-Configuration {
    param([string]$ConfigPath)
    
    $configFile = Join-Path $RepoPath $ConfigPath
    
    if (Test-Path $configFile) {
        try {
            if ($YamlAvailable -and $ConfigPath.EndsWith(".yaml")) {
                $loadedConfig = Get-Content $configFile | ConvertFrom-Yaml
            }
            else {
                # Fallback to JSON if YAML not available
                $jsonConfigFile = $configFile -replace ".yaml$", ".json"
                if (Test-Path $jsonConfigFile) {
                    $loadedConfig = Get-Content $jsonConfigFile | ConvertFrom-Json
                }
                else {
                    Write-Log "Configuration file not found, using defaults" "WARN"
                    return $Script:Config
                }
            }
            
            # Merge with defaults
            foreach ($key in $loadedConfig.PSObject.Properties.Name) {
                $Script:Config[$key] = $loadedConfig.$key
            }
            
            Write-Log "Configuration loaded from $configFile"
        }
        catch {
            Write-Log "Error loading configuration: $_" "ERROR"
            Write-Log "Using default configuration" "WARN"
        }
    }
    else {
        Write-Log "Configuration file not found: $configFile" "WARN"
        Write-Log "Using default configuration"
    }
    
    return $Script:Config
}

# Git command execution
function Invoke-GitCommand {
    param(
        [string[]]$Arguments,
        [switch]$IgnoreErrors
    )
    
    $gitCommand = "git"
    $allArgs = $Arguments -join " "
    
    Write-Log "Executing: git $allArgs" "DEBUG"
    
    try {
        $result = & $gitCommand @Arguments 2>&1
        
        if ($LASTEXITCODE -ne 0 -and -not $IgnoreErrors) {
            throw "Git command failed: git $allArgs`nError: $result"
        }
        
        return $result
    }
    catch {
        if (-not $IgnoreErrors) {
            Write-Log "Git command failed: $_" "ERROR"
            throw $_
        }
        return $null
    }
}

# Pre-merge validation
function Test-PreMergeConditions {
    param(
        [string]$SourceBranch,
        [string]$TargetBranch
    )
    
    Write-Log "Running pre-merge validation"
    
    $validation = @{
        passed = $true
        checks = @{}
        errors = @()
        warnings = @()
    }
    
    try {
        # Check if branches exist
        $sourceBranchExists = Test-BranchExists -BranchName $SourceBranch
        $targetBranchExists = Test-BranchExists -BranchName $TargetBranch
        
        $validation.checks.source_branch_exists = $sourceBranchExists
        $validation.checks.target_branch_exists = $targetBranchExists
        
        if (-not $sourceBranchExists) {
            $validation.errors += "Source branch does not exist: $SourceBranch"
            $validation.passed = $false
        }
        
        if (-not $targetBranchExists) {
            $validation.errors += "Target branch does not exist: $TargetBranch"
            $validation.passed = $false
        }
        
        # Check if target branch is protected
        if ($TargetBranch -in $Script:Config.branch_settings.protected_branches) {
            $validation.checks.target_protected = $true
            $validation.warnings += "Target branch is protected: $TargetBranch"
        }
        
        # Check for uncommitted changes
        $hasUncommittedChanges = Test-UncommittedChanges
        $validation.checks.clean_working_directory = -not $hasUncommittedChanges
        
        if ($hasUncommittedChanges) {
            $validation.errors += "Working directory has uncommitted changes"
            $validation.passed = $false
        }
        
        # Check if source is ahead of target
        if ($sourceBranchExists -and $targetBranchExists) {
            $commitsAhead = Get-CommitsAhead -SourceBranch $SourceBranch -TargetBranch $TargetBranch
            $validation.checks.commits_ahead = $commitsAhead
            
            if ($commitsAhead -eq 0) {
                $validation.warnings += "Source branch has no new commits"
            }
        }
        
        # Run quality gates if enabled
        if ($Script:Config.merge_settings.run_tests_before_merge) {
            $qualityResult = Invoke-QualityGates
            $validation.quality_gates = $qualityResult
            
            if (-not $qualityResult.passed) {
                $validation.passed = $false
                $validation.errors += "Quality gates failed"
            }
        }
        
        Write-Log "Pre-merge validation completed: Passed=$($validation.passed)"
        
    }
    catch {
        Write-Log "Pre-merge validation error: $_" "ERROR"
        $validation.passed = $false
        $validation.errors += "Validation error: $_"
    }
    
    return $validation
}

# Execute merge operation
function Invoke-MergeOperation {
    param(
        [string]$SourceBranch,
        [string]$TargetBranch,
        [string]$Strategy
    )
    
    Write-Log "Executing merge operation with strategy: $Strategy"
    
    $mergeResult = @{
        status = "unknown"
        conflicts = @()
        merged_files = @()
        command_output = ""
    }
    
    try {
        # Ensure we're on the target branch
        Invoke-GitCommand -Arguments @("checkout", $TargetBranch)
        
        # Pull latest changes
        Invoke-GitCommand -Arguments @("pull", "origin", $TargetBranch) -IgnoreErrors
        
        # Prepare merge command
        $mergeArgs = @("merge", $SourceBranch)
        
        switch ($Strategy) {
            "no-ff" { $mergeArgs += "--no-ff" }
            "squash" { $mergeArgs += "--squash" }
            "ff-only" { $mergeArgs += "--ff-only" }
        }
        
        try {
            $result = Invoke-GitCommand -Arguments $mergeArgs
            $mergeResult.command_output = $result -join "`n"
            $mergeResult.status = "success"
            
            # Get list of merged files
            $mergedFiles = Get-MergedFiles -SourceBranch $SourceBranch -TargetBranch $TargetBranch
            $mergeResult.merged_files = $mergedFiles
            
        }
        catch {
            $errorMessage = $_.Exception.Message
            
            if ($errorMessage -like "*conflict*" -or $errorMessage -like "*merge conflict*") {
                # Handle merge conflicts
                $conflicts = Get-MergeConflicts
                $mergeResult.conflicts = $conflicts
                $mergeResult.status = "conflicts"
                $mergeResult.command_output = $errorMessage
            }
            else {
                throw $_
            }
        }
        
    }
    catch {
        Write-Log "Merge operation failed: $_" "ERROR"
        $mergeResult.status = "error"
        $mergeResult.error = $_.Exception.Message
    }
    
    return $mergeResult
}

# Resolve merge conflicts
function Resolve-MergeConflicts {
    param([array]$Conflicts)
    
    Write-Log "Resolving $($Conflicts.Count) conflicts"
    
    $resolutionResult = @{
        status = "unknown"
        resolved_conflicts = @()
        unresolved_conflicts = @()
        resolution_summary = @{}
    }
    
    try {
        foreach ($conflict in $Conflicts) {
            $filePath = $conflict.file
            $conflictType = $conflict.type
            
            # Check if file requires manual review
            if (Test-RequiresManualReview -FilePath $filePath) {
                $resolutionResult.unresolved_conflicts += $conflict
                continue
            }
            
            # Determine resolution strategy
            $resolutionStrategy = Get-ResolutionStrategy -FilePath $filePath -ConflictType $conflictType
            
            $resolved = $false
            
            switch ($resolutionStrategy) {
                "prefer_incoming" {
                    $resolved = Resolve-PreferIncoming -FilePath $filePath
                }
                "prefer_current" {
                    $resolved = Resolve-PreferCurrent -FilePath $filePath
                }
                "smart_merge" {
                    $resolved = Resolve-SmartMerge -FilePath $filePath -Conflict $conflict
                }
                default {
                    $resolved = $false
                }
            }
            
            if ($resolved) {
                $resolutionResult.resolved_conflicts += @{
                    file = $filePath
                    strategy = $resolutionStrategy
                    timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
                }
                
                # Stage resolved file
                Invoke-GitCommand -Arguments @("add", $filePath)
            }
            else {
                $resolutionResult.unresolved_conflicts += $conflict
            }
        }
        
        # Update status based on resolution results
        if ($resolutionResult.unresolved_conflicts.Count -eq 0) {
            $resolutionResult.status = "resolved"
            
            # Complete the merge
            Invoke-GitCommand -Arguments @("commit", "--no-edit")
        }
        elseif ($resolutionResult.resolved_conflicts.Count -gt 0) {
            $resolutionResult.status = "partially_resolved"
        }
        else {
            $resolutionResult.status = "unresolved"
        }
        
        $resolutionResult.resolution_summary = @{
            total_conflicts = $Conflicts.Count
            resolved = $resolutionResult.resolved_conflicts.Count
            unresolved = $resolutionResult.unresolved_conflicts.Count
        }
        
        Write-Log "Conflict resolution completed: $($resolutionResult.status)"
        
    }
    catch {
        Write-Log "Conflict resolution failed: $_" "ERROR"
        $resolutionResult.status = "error"
        $resolutionResult.error = $_.Exception.Message
    }
    
    return $resolutionResult
}

# Post-merge validation
function Test-PostMergeConditions {
    Write-Log "Running post-merge validation"
    
    $validation = @{
        passed = $true
        checks = @{}
        errors = @()
    }
    
    try {
        # Run quality gates
        if ($Script:Config.quality_gates.run_unit_tests) {
            $testResult = Invoke-UnitTests
            $validation.checks.unit_tests = $testResult
            
            if (-not $testResult.passed) {
                $validation.passed = $false
                $validation.errors += "Unit tests failed"
            }
        }
        
        if ($Script:Config.quality_gates.run_linting) {
            $lintResult = Invoke-Linting
            $validation.checks.linting = $lintResult
            
            if (-not $lintResult.passed) {
                $validation.passed = $false
                $validation.errors += "Linting failed"
            }
        }
        
        if ($Script:Config.quality_gates.run_integration_tests) {
            $integrationResult = Invoke-IntegrationTests
            $validation.checks.integration_tests = $integrationResult
            
            if (-not $integrationResult.passed) {
                $validation.passed = $false
                $validation.errors += "Integration tests failed"
            }
        }
        
        # Check system integrity
        $integrityResult = Test-SystemIntegrity
        $validation.checks.system_integrity = $integrityResult
        
        if (-not $integrityResult.passed) {
            $validation.passed = $false
            $validation.errors += "System integrity check failed"
        }
        
        Write-Log "Post-merge validation completed: Passed=$($validation.passed)"
        
    }
    catch {
        Write-Log "Post-merge validation error: $_" "ERROR"
        $validation.passed = $false
        $validation.errors += "Validation error: $_"
    }
    
    return $validation
}

# Main merge automation function
function Start-AutomatedMerge {
    param(
        [string]$SourceBranch,
        [string]$TargetBranch,
        [string]$Strategy
    )
    
    $mergeSession = @{
        session_id = "merge_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        source_branch = $SourceBranch
        target_branch = $TargetBranch
        strategy = $Strategy
        start_time = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        status = "in_progress"
    }
    
    Write-Log "Starting automated merge: $SourceBranch -> $TargetBranch"
    
    try {
        # Pre-merge validation
        $validationResult = Test-PreMergeConditions -SourceBranch $SourceBranch -TargetBranch $TargetBranch
        $mergeSession.pre_validation = $validationResult
        
        if (-not $validationResult.passed) {
            $mergeSession.status = "failed"
            $mergeSession.error = "Pre-merge validation failed"
            return $mergeSession
        }
        
        # Create backup if configured
        if ($Script:Config.merge_settings.backup_before_merge) {
            $backupResult = New-MergeBackup -BranchName $TargetBranch
            $mergeSession.backup = $backupResult
        }
        
        # Execute merge
        $mergeResult = Invoke-MergeOperation -SourceBranch $SourceBranch -TargetBranch $TargetBranch -Strategy $Strategy
        $mergeSession.merge_operation = $mergeResult
        
        if ($mergeResult.status -eq "conflicts") {
            # Handle conflicts
            $conflictResolution = Resolve-MergeConflicts -Conflicts $mergeResult.conflicts
            $mergeSession.conflict_resolution = $conflictResolution
            
            if ($conflictResolution.status -ne "resolved") {
                $mergeSession.status = "conflicts_unresolved"
                return $mergeSession
            }
        }
        
        # Post-merge validation
        if ($mergeResult.status -in @("success", "conflicts_resolved")) {
            $postValidation = Test-PostMergeConditions
            $mergeSession.post_validation = $postValidation
            
            if (-not $postValidation.passed) {
                # Rollback if validation fails
                $rollbackResult = Invoke-MergeRollback -MergeSession $mergeSession
                $mergeSession.rollback = $rollbackResult
                $mergeSession.status = "rollback_completed"
                return $mergeSession
            }
        }
        
        # Finalize merge
        $finalizationResult = Complete-MergeFinalization -MergeSession $mergeSession
        $mergeSession.finalization = $finalizationResult
        $mergeSession.status = "completed"
        
        Write-Log "Merge completed successfully: $SourceBranch -> $TargetBranch"
        
    }
    catch {
        Write-Log "Merge failed: $_" "ERROR"
        $mergeSession.status = "error"
        $mergeSession.error = $_.Exception.Message
        
        # Attempt rollback on error
        try {
            $rollbackResult = Invoke-MergeRollback -MergeSession $mergeSession
            $mergeSession.rollback = $rollbackResult
        }
        catch {
            Write-Log "Rollback failed: $_" "ERROR"
            $mergeSession.rollback_error = $_.Exception.Message
        }
    }
    finally {
        $mergeSession.end_time = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        Save-MergeSession -MergeSession $mergeSession
    }
    
    return $mergeSession
}

# Helper functions
function Test-BranchExists {
    param([string]$BranchName)
    
    try {
        Invoke-GitCommand -Arguments @("rev-parse", "--verify", "refs/heads/$BranchName") | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-UncommittedChanges {
    try {
        $result = Invoke-GitCommand -Arguments @("status", "--porcelain")
        return ($result -join "").Trim().Length -gt 0
    }
    catch {
        return $true  # Assume there are changes if we can't check
    }
}

function Get-CommitsAhead {
    param(
        [string]$SourceBranch,
        [string]$TargetBranch
    )
    
    try {
        $result = Invoke-GitCommand -Arguments @("rev-list", "--count", "$TargetBranch..$SourceBranch")
        return [int]($result | Select-Object -First 1)
    }
    catch {
        return 0
    }
}

function Invoke-QualityGates {
    $qualityResult = @{
        passed = $true
        checks = @{}
    }
    
    try {
        if ($Script:Config.quality_gates.run_linting) {
            $lintResult = Invoke-Linting
            $qualityResult.checks.linting = $lintResult
            if (-not $lintResult.passed) {
                $qualityResult.passed = $false
            }
        }
        
        if ($Script:Config.quality_gates.run_unit_tests) {
            $testResult = Invoke-UnitTests
            $qualityResult.checks.unit_tests = $testResult
            if (-not $testResult.passed) {
                $qualityResult.passed = $false
            }
        }
        
    }
    catch {
        Write-Log "Quality gates error: $_" "ERROR"
        $qualityResult.passed = $false
        $qualityResult.error = $_.Exception.Message
    }
    
    return $qualityResult
}

function Invoke-Linting {
    try {
        $result = Start-Process -FilePath "flake8" -ArgumentList "." -Wait -PassThru -NoNewWindow -RedirectStandardOutput "lint_output.txt" -RedirectStandardError "lint_errors.txt"
        
        $output = if (Test-Path "lint_output.txt") { Get-Content "lint_output.txt" } else { "" }
        $errors = if (Test-Path "lint_errors.txt") { Get-Content "lint_errors.txt" } else { "" }
        
        # Cleanup temp files
        Remove-Item "lint_output.txt", "lint_errors.txt" -ErrorAction SilentlyContinue
        
        return @{
            passed = $result.ExitCode -eq 0
            output = $output -join "`n"
            errors = $errors -join "`n"
        }
    }
    catch {
        return @{
            passed = $false
            error = $_.Exception.Message
        }
    }
}

function Invoke-UnitTests {
    try {
        $result = Start-Process -FilePath "python" -ArgumentList "-m", "unittest", "discover", "tests/", "-v" -Wait -PassThru -NoNewWindow -RedirectStandardOutput "test_output.txt" -RedirectStandardError "test_errors.txt"
        
        $output = if (Test-Path "test_output.txt") { Get-Content "test_output.txt" } else { "" }
        $errors = if (Test-Path "test_errors.txt") { Get-Content "test_errors.txt" } else { "" }
        
        # Cleanup temp files
        Remove-Item "test_output.txt", "test_errors.txt" -ErrorAction SilentlyContinue
        
        return @{
            passed = $result.ExitCode -eq 0
            output = $output -join "`n"
            errors = $errors -join "`n"
        }
    }
    catch {
        return @{
            passed = $false
            error = $_.Exception.Message
        }
    }
}

function Invoke-IntegrationTests {
    try {
        $result = Start-Process -FilePath "python" -ArgumentList "integration.py", "validate" -Wait -PassThru -NoNewWindow -RedirectStandardOutput "integration_output.txt" -RedirectStandardError "integration_errors.txt"
        
        $output = if (Test-Path "integration_output.txt") { Get-Content "integration_output.txt" } else { "" }
        $errors = if (Test-Path "integration_errors.txt") { Get-Content "integration_errors.txt" } else { "" }
        
        # Cleanup temp files
        Remove-Item "integration_output.txt", "integration_errors.txt" -ErrorAction SilentlyContinue
        
        return @{
            passed = $result.ExitCode -eq 0
            output = $output -join "`n"
            errors = $errors -join "`n"
        }
    }
    catch {
        return @{
            passed = $false
            error = $_.Exception.Message
        }
    }
}

function Test-SystemIntegrity {
    $integrityChecks = @{
        passed = $true
        checks = @{}
    }
    
    try {
        # Check if critical files exist
        $criticalFiles = @("integration.py", "requirements.txt", "README.md")
        
        foreach ($fileName in $criticalFiles) {
            $filePath = Join-Path $RepoPath $fileName
            $exists = Test-Path $filePath
            $integrityChecks.checks."$($fileName)_exists" = $exists
            
            if (-not $exists) {
                $integrityChecks.passed = $false
            }
        }
        
        # Check if Python can import key modules
        try {
            $result = python -c "import agent_register_sync; print('success')" 2>&1
            $integrityChecks.checks.agent_sync_importable = $result -like "*success*"
            
            if (-not $integrityChecks.checks.agent_sync_importable) {
                $integrityChecks.passed = $false
            }
        }
        catch {
            $integrityChecks.checks.agent_sync_importable = $false
            $integrityChecks.passed = $false
        }
        
    }
    catch {
        $integrityChecks.passed = $false
        $integrityChecks.error = $_.Exception.Message
    }
    
    return $integrityChecks
}

function New-MergeBackup {
    param([string]$BranchName)
    
    try {
        # Get current commit hash
        $commitHash = (Invoke-GitCommand -Arguments @("rev-parse", "HEAD")).Trim()
        
        # Create backup tag
        $backupTag = "backup_$($BranchName)_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Invoke-GitCommand -Arguments @("tag", $backupTag)
        
        Write-Log "Created backup tag: $backupTag"
        
        return @{
            status = "created"
            commit_hash = $commitHash
            backup_tag = $backupTag
        }
        
    }
    catch {
        Write-Log "Backup creation failed: $_" "ERROR"
        return @{
            status = "failed"
            error = $_.Exception.Message
        }
    }
}

function Get-MergeConflicts {
    $conflicts = @()
    
    try {
        # Get list of conflicted files
        $result = Invoke-GitCommand -Arguments @("diff", "--name-only", "--diff-filter=U") -IgnoreErrors
        $conflictedFiles = $result | Where-Object { $_ -and $_.Trim() -ne "" }
        
        foreach ($filePath in $conflictedFiles) {
            $conflictInfo = @{
                file = $filePath.Trim()
                type = "content_conflict"
                detected_at = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
            }
            $conflicts += $conflictInfo
        }
        
    }
    catch {
        Write-Log "Conflict detection failed: $_" "ERROR"
    }
    
    return $conflicts
}

function Get-MergedFiles {
    param(
        [string]$SourceBranch,
        [string]$TargetBranch
    )
    
    try {
        $result = Invoke-GitCommand -Arguments @("diff", "--name-only", "$TargetBranch@{1}", $TargetBranch) -IgnoreErrors
        return $result | Where-Object { $_ -and $_.Trim() -ne "" }
    }
    catch {
        return @()
    }
}

function Test-RequiresManualReview {
    param([string]$FilePath)
    
    $manualReviewFiles = $Script:Config.conflict_resolution.manual_review_required
    
    foreach ($pattern in $manualReviewFiles) {
        if ($FilePath -like "*$pattern*") {
            return $true
        }
    }
    
    return $false
}

function Get-ResolutionStrategy {
    param(
        [string]$FilePath,
        [string]$ConflictType
    )
    
    # Check prefer_incoming patterns
    foreach ($pattern in $Script:Config.conflict_resolution.prefer_incoming_for) {
        if ($FilePath -like "*$($pattern.Replace('*', ''))*") {
            return "prefer_incoming"
        }
    }
    
    # Check prefer_current patterns
    foreach ($pattern in $Script:Config.conflict_resolution.prefer_current_for) {
        if ($FilePath -like "*$($pattern.Replace('*', ''))*") {
            return "prefer_current"
        }
    }
    
    # Default to smart merge if auto resolution is enabled
    if ($Script:Config.conflict_resolution.auto_resolve_simple) {
        return "smart_merge"
    }
    
    return "manual"
}

function Resolve-PreferIncoming {
    param([string]$FilePath)
    
    try {
        Invoke-GitCommand -Arguments @("checkout", "--theirs", $FilePath)
        Write-Log "Resolved conflict using prefer_incoming: $FilePath"
        return $true
    }
    catch {
        Write-Log "Failed to resolve $FilePath with prefer_incoming: $_" "ERROR"
        return $false
    }
}

function Resolve-PreferCurrent {
    param([string]$FilePath)
    
    try {
        Invoke-GitCommand -Arguments @("checkout", "--ours", $FilePath)
        Write-Log "Resolved conflict using prefer_current: $FilePath"
        return $true
    }
    catch {
        Write-Log "Failed to resolve $FilePath with prefer_current: $_" "ERROR"
        return $false
    }
}

function Resolve-SmartMerge {
    param(
        [string]$FilePath,
        [hashtable]$Conflict
    )
    
    try {
        # This is a simplified smart merge - in practice, this would be more sophisticated
        # For now, we'll try to use git's merge tools
        $mergeTools = $Script:Config.conflict_resolution.merge_tools
        
        if ("diff3" -in $mergeTools) {
            # Use diff3 style merge
            Invoke-GitCommand -Arguments @("config", "merge.conflictstyle", "diff3") -IgnoreErrors
        }
        
        # For simple cases, prefer incoming by default
        return Resolve-PreferIncoming -FilePath $FilePath
        
    }
    catch {
        Write-Log "Smart merge failed for $FilePath : $_" "ERROR"
        return $false
    }
}

function Complete-MergeFinalization {
    param([hashtable]$MergeSession)
    
    Write-Log "Finalizing merge operation"
    
    $finalizationResult = @{
        status = "completed"
        actions_taken = @()
    }
    
    try {
        $targetBranch = $MergeSession.target_branch
        
        # Push changes to remote
        Invoke-GitCommand -Arguments @("push", "origin", $targetBranch)
        $finalizationResult.actions_taken += "pushed_to_remote"
        
        # Create merge tag if configured
        if ($Script:Config.merge_settings.create_merge_tags) {
            $tagName = "merge_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Invoke-GitCommand -Arguments @("tag", $tagName)
            Invoke-GitCommand -Arguments @("push", "origin", $tagName)
            $finalizationResult.actions_taken += "created_tag_$tagName"
        }
        
        # Send notifications
        if ($Script:Config.notification_settings.notify_on_success) {
            Send-MergeNotification -Type "merge_success" -MergeSession $MergeSession
            $finalizationResult.actions_taken += "sent_success_notification"
        }
        
        Write-Log "Merge finalization completed successfully"
        
    }
    catch {
        Write-Log "Merge finalization error: $_" "ERROR"
        $finalizationResult.status = "error"
        $finalizationResult.error = $_.Exception.Message
    }
    
    return $finalizationResult
}

function Invoke-MergeRollback {
    param([hashtable]$MergeSession)
    
    Write-Log "Rolling back merge operation"
    
    $rollbackResult = @{
        status = "completed"
        actions_taken = @()
    }
    
    try {
        # Abort merge if in progress
        try {
            Invoke-GitCommand -Arguments @("merge", "--abort") -IgnoreErrors
            $rollbackResult.actions_taken += "aborted_merge"
        }
        catch {
            # No merge in progress
        }
        
        # Reset to previous state if backup exists
        if ($MergeSession.backup -and $MergeSession.backup.status -eq "created") {
            $backupCommit = $MergeSession.backup.commit_hash
            Invoke-GitCommand -Arguments @("reset", "--hard", $backupCommit)
            $rollbackResult.actions_taken += "reset_to_backup"
        }
        
        # Send failure notification
        if ($Script:Config.notification_settings.notify_on_failure) {
            Send-MergeNotification -Type "merge_failure" -MergeSession $MergeSession
            $rollbackResult.actions_taken += "sent_failure_notification"
        }
        
        Write-Log "Merge rollback completed"
        
    }
    catch {
        Write-Log "Rollback error: $_" "ERROR"
        $rollbackResult.status = "error"
        $rollbackResult.error = $_.Exception.Message
    }
    
    return $rollbackResult
}

function Send-MergeNotification {
    param(
        [string]$Type,
        [hashtable]$MergeSession
    )
    
    try {
        $webhookUrl = $Script:Config.notification_settings.webhook_url
        if ($webhookUrl) {
            # This would send actual notifications
            Write-Log "Would send $Type notification to $webhookUrl"
        }
        else {
            Write-Log "Notification: $Type - $($MergeSession.session_id)"
        }
    }
    catch {
        Write-Log "Notification failed: $_" "ERROR"
    }
}

function Save-MergeSession {
    param([hashtable]$MergeSession)
    
    try {
        $logFile = Join-Path $RepoPath "logs\merge_sessions_ps.json"
        $sessionJson = $MergeSession | ConvertTo-Json -Depth 10
        
        # Ensure logs directory exists
        $logsDir = Split-Path $logFile -Parent
        if (-not (Test-Path $logsDir)) {
            New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
        }
        
        $sessionJson | Add-Content -Path $logFile
        Write-Log "Merge session saved to $logFile"
    }
    catch {
        Write-Log "Failed to save merge session: $_" "ERROR"
    }
}

function Get-MergeStatus {
    $status = @{
        merge_automation_enabled = $Script:Config.merge_settings.auto_merge_enabled
        powershell_version = $PSVersionTable.PSVersion.ToString()
        git_available = $true
        last_operation = "never"
    }
    
    try {
        # Check if git is available
        git --version | Out-Null
    }
    catch {
        $status.git_available = $false
    }
    
    # Check for recent operations
    try {
        $logFile = Join-Path $RepoPath "logs\merge_sessions_ps.json"
        if (Test-Path $logFile) {
            $lastLine = Get-Content $logFile | Select-Object -Last 1
            if ($lastLine) {
                $lastSession = $lastLine | ConvertFrom-Json
                $status.last_operation = $lastSession.start_time
            }
        }
    }
    catch {
        # Ignore errors getting last operation
    }
    
    return $status
}

# Main execution
function Main {
    try {
        # Ensure we're in a git repository
        Push-Location $RepoPath
        
        # Load configuration
        $Script:Config = Load-Configuration -ConfigPath $ConfigPath
        
        # Ensure logs directory exists
        $logsDir = Join-Path $RepoPath "logs"
        if (-not (Test-Path $logsDir)) {
            New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
        }
        
        Write-Log "=== EpochCore RAS Merge Automation PowerShell ==="
        Write-Log "Repository: $RepoPath"
        
        if ($Status) {
            $status = Get-MergeStatus
            Write-Host ($status | ConvertTo-Json -Depth 5)
            return 0
        }
        
        if ($Validate) {
            Write-Log "Running validation checks..."
            
            # Check git availability
            try {
                $gitVersion = git --version
                Write-Log "Git version: $gitVersion"
            }
            catch {
                Write-Log "Git not available!" "ERROR"
                return 1
            }
            
            # Check PowerShell version
            Write-Log "PowerShell version: $($PSVersionTable.PSVersion)"
            
            # Check repository status
            try {
                $repoStatus = Invoke-GitCommand -Arguments @("status", "--porcelain")
                if ($repoStatus) {
                    Write-Log "Repository has uncommitted changes" "WARN"
                }
                else {
                    Write-Log "Repository is clean"
                }
            }
            catch {
                Write-Log "Not in a git repository!" "ERROR"
                return 1
            }
            
            Write-Log "Validation completed successfully"
            return 0
        }
        
        if (-not $SourceBranch) {
            Write-Host "Usage: merge_automation.ps1 -SourceBranch <source> [-TargetBranch <target>] [-Strategy <strategy>]"
            Write-Host "       merge_automation.ps1 -Status"
            Write-Host "       merge_automation.ps1 -Validate"
            return 1
        }
        
        # Execute automated merge
        $result = Start-AutomatedMerge -SourceBranch $SourceBranch -TargetBranch $TargetBranch -Strategy $Strategy
        
        # Output result
        Write-Host ($result | ConvertTo-Json -Depth 10)
        
        # Return appropriate exit code
        switch ($result.status) {
            "completed" { return 0 }
            "conflicts_unresolved" { return 2 }
            default { return 1 }
        }
        
    }
    catch {
        Write-Log "Fatal error: $_" "ERROR"
        return 1
    }
    finally {
        Pop-Location
    }
}

# Execute main function
exit (Main)