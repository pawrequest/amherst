function updateManualFields() {
    const selectedOption = document.getElementById('address-select').value;
    const addressData = JSON.parse(selectedOption);
    console.log('Address data:', addressData)

    document.getElementById('address_line1').value = addressData.address_line1 || '';
    document.getElementById('address_line2').value = addressData.address_line2 || '';
    document.getElementById('address_line3').value = addressData.address_line3 || '';
    document.getElementById('town').value = addressData.town || '';
    document.getElementById('postcode').value = addressData.postcode || '';
}

function loadCandidates() {
    console.log('Loading candidates');
    const postcode = document.getElementById('postcode').value;
    fetch(`/jinji/get_candidates?postcode=${postcode}`)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            const addressSelect = document.getElementById('address-select');
            addressSelect.innerHTML = '';
            for (const [key, value] of Object.entries(data)) {
                console.log('key:', key, 'val:', value);
                const option = document.createElement('option');
                option.value = value;
                option.textContent = key;
                addressSelect.appendChild(option);
            }
            updateManualFields();
        });
}