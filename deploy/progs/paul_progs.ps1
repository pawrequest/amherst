$appName = "paul_r"
$SourceDir = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
$TargetDir = "C:\Program Files\" + $appName
$script:DataDir = $env:LOCALAPPDATA + "\" + $appName
$DateTime = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path -Path $script:DataDir -ChildPath "DeployLog_$DateTime.txt"

function IsUninstalling{
    $mode = Read-Host -Prompt "[I]nstall or [U]ninstall?"
    $mode = $mode.Trim().ToLower()
    if ($mode -eq "u")
    {
        return $true
    }
    elseif ($mode -eq "i")
    {
        return $false
    }
    else
    {
        Write-Host "Invalid entry. Please enter 'i' or 'u'."
        IsUninstalling
    }

}


function CheckAdmin($scriptPath = $PSCommandPath)
{
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]"Administrator"))
    {
        Write-Host "Restarting with Administrator privileges."
        $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
        if ($Uninstall)
        {
            $arguments += " -Uninstall"
        }
        Start-Process powershell -ArgumentList $arguments -Verb RunAs
        exit
    }
}


function CreateDataDir
{
    If (-Not (Test-Path -Path $script:DataDir))
    {
        New-Item -Path $script:DataDir -ItemType Directory | Out-Null
    }
}

function RemoveEnvVars()
{
    [System.Environment]::SetEnvironmentVariable("SHIP_ENV", $null, [System.EnvironmentVariableTarget]::User)
    [System.Environment]::SetEnvironmentVariable("AM_ENV", $null, [System.EnvironmentVariableTarget]::User)
    "Environment variables set" | Out-File -FilePath $LogFile -Encoding UTF8 -Append

}
function SetEnvVars()
{
    [System.Environment]::SetEnvironmentVariable("SHIP_ENV", $script:DataDir + "\envs\pf_live.env", [System.EnvironmentVariableTarget]::User)
    [System.Environment]::SetEnvironmentVariable("AM_ENV", $script:DataDir + "\envs\am_live.env", [System.EnvironmentVariableTarget]::User)
    "Environment variables set" | Out-File -FilePath $LogFile -Encoding UTF8 -Append

}


function ConfirmActions
{
    if ($Uninstall)
    {
        Write-Host "You are about to uninstall paul's apps."
        Write-Host "This will delete $TargetDir"
        Write-Host "This will remove Windows Defender exclusion for $TargetDir"
        Write-Host "This will remove environment variables"
    }
    else
    {
        Write-Host "You are about to install paul's apps."
        Write-Host "This will create or modify $TargetDir"
        Write-Host "This will add Windows Defender exclusion for $TargetDir"
        Write-Host "This will set environment variables"
    }
    $confirmation = Read-Host -Prompt "[y] to continue, any other entry to cancel"
    if ($confirmation.ToLower() -eq "y")
    {
#        return $true
    }
    else
    {
        Write-Host "Operation canceled by user."
        exit
    }

}

function InstallProgs
{
    # Install
    # Create target directory if it doesn't exist
    If (-Not (Test-Path -Path $TargetDir))
    {
        New-Item -Path $TargetDir -ItemType Directory | Out-Null
    }

    # Copy files and folders recursively
    Get-ChildItem -Path $SourceDir -Recurse | ForEach-Object {
        $Destination = Join-Path -Path $TargetDir -ChildPath $_.FullName.Substring($SourceDir.Length).TrimStart("\")
        # Check if the item is a directory
        If ($_.PSIsContainer -and -Not (Test-Path -Path $Destination))
        {
            New-Item -ItemType Directory -Path $Destination | Out-Null
        }

        # Copy the file or directory to the destination
        If (-Not $_.PSIsContainer)
        {
            Copy-Item -Path $_.FullName -Destination $Destination -Force
            "Copied: $( $_.FullName ) -> $Destination" | Out-File -FilePath $LogFile -Encoding UTF8 -Append
        }
    }
    $Additional = @{
        "\\AMHERSTMAIN\amherst\paul_r\.internal\envs\pf_live.env" = $script:DataDir + "\envs"
        "\\AMHERSTMAIN\amherst\paul_r\.internal\envs\am_live.env" = $script:DataDir + "\envs"
    }

    # Copy additional files
    foreach ($key in $Additional.Keys)
    {
        $value = $Additional[$key]
        If (-Not (Test-Path -Path $value))
        {
            New-Item -Path $value -ItemType Directory | Out-Null
        }
        Copy-Item -Path $key -Destination $value -Force
        "Copied: $key -> $( $value )" | Out-File -FilePath $LogFile -Encoding UTF8 -Append
    }

    SetEnvVars

    # Add Defender exclusion
    Add-MpPreference -ExclusionPath $TargetDir
    "Windows Defender exclusion added for $TargetDir" | Out-File -FilePath $LogFile -Encoding UTF8 -Append
}
function MaybeRemoveDataDir
{
    $confirmation = Read-Host -Prompt "Delete logs and user data in ${script:DataDir}? [y/n]"
    if ($confirmation -eq "y")
    {
        Remove-Item -Path $script:DataDir -Recurse -Force
        Write-Host "Deleted $script:DataDir"
    }
}
function UninstallProgs
{
    Write-Host "Uninstalling..."
    if (Test-Path -Path $TargetDir)
    {
        Remove-Item -Path $TargetDir -Recurse -Force
        "Removed target directory: $TargetDir" | Out-File -FilePath $LogFile -Encoding UTF8 -Append
    }

    Remove-MpPreference -ExclusionPath $TargetDir
    "Windows Defender exclusion removed for $TargetDir" | Out-File -FilePath $LogFile -Encoding UTF8 -Append

    RemoveEnvVars
    "Environment variables removed" | Out-File -FilePath $LogFile -Encoding UTF8 -Append
}


CheckAdmin
CreateDataDir
"Deployment started at $DateTime" | Out-File -FilePath $LogFile -Encoding UTF8 -Append
$Uninstall = IsUninstalling
ConfirmActions
if ($Uninstall)
{
    UninstallProgs
    MaybeRemoveDataDir
}
else
{
    InstallProgs
}
Write-Host "Process complete at $( Get-Date )"
Read-Host -Prompt "[Enter] to exit"
