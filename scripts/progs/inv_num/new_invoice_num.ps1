$INV_FOLDER = 'R:\ACCOUNTS\invoices'

function Get-InvNums {
    $files = Get-ChildItem -Path $INV_FOLDER
    $inv_numbers = @{}

    foreach ($file in $files) {
        if ($file.Name -match '^[Aa](\d{5}).*$') {
            $inv_numbers[$Matches[1]] = $true
        }
    }
    return $inv_numbers.Keys
}

function Has-20After {
    param (
        [int]$index,
        [int[]]$nums
    )

    $tally = 0
    while ($tally -lt 20) {
        $num = $nums[$index]
        $next_num = $nums[$index + 1]
        if ($num -eq ($next_num + 1)) {
            $tally++
            $index++
        }
        else {
            return $false
        }
    }
    return $true
}

$inv_numbers = Get-InvNums
$inv_numbers = $inv_numbers | Sort-Object -Descending

for ($index = 0; $index -lt $inv_numbers.Length; $index++) {
    if (Has-20After -index $index -nums $inv_numbers) {
        $new_filename = "A" + ([int]$inv_numbers[$index] + 1)
        Write-Output "`n`n`t$new_filename `n`tIs the next available Invoice number `n`tand is stored in your clipboard"
	Set-Clipboard -Value $new_filename

        break
    }
}
