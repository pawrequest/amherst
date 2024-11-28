$INV_FOLDER = 'R:\ACCOUNTS\invoices'

function Get-InvNums {
    $files = Get-ChildItem -Path $INV_FOLDER
    $inv_numbers = @()

    foreach ($file in $files) {
        if ($file.Name -match '^[Aa](\d{5}).*$') {
            $inv_numbers += [int]$Matches[1]
        }
    }

    $inv_numbers = $inv_numbers | Sort-Object -Unique
        
    return $inv_numbers
}

function Sequential-Sublists {
    param([int[]]$num_set)
    $num_set = $num_set | Sort-Object
    $sequences = @()
    $current_sequence = @($num_set[0])

    foreach ($num in $num_set[1..$num_set.Length]) {
        if ($num -eq ($current_sequence[-1] + 1)) {
            $current_sequence += $num
        }
        else {
            if ($current_sequence.Length -gt 100) {
                $sequences += ,$current_sequence
            }
            $current_sequence = @($num)
        }
    }

    return $sequences
}

$inv_numbers = Get-InvNums
if ($inv_numbers.Length -eq 0) { Write-Host "No matching invoice numbers found."; exit }

$sequences = Sequential-Sublists -num_set $inv_numbers
if ($sequences.Length -eq 0) { Write-Host "No sequence found with more than 100 elements."; exit }

$latest_sequence = $sequences[-1]
$latest_inv_number = $latest_sequence[-1]
$new_num = $latest_inv_number + 1
$new_filename = "A$new_num"
# Write-Host $new_filename
Write-Output $new_filename 

