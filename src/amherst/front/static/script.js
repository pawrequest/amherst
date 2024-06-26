/**
 * @typedef {Object} Address
 * @property {string} AddressLine1
 * @property {string} AddressLine2
 * @property {string} AddressLine3
 * @property {string} Town
 * @property {string} Postcode
 * @property {string} Country
 */

/**
 * @typedef {Object} AddressChoice
 * @property {Address} Address
 * @property {number} Score
 */
function updateManualFields() {
    const selectedOption = document.getElementById('address-select').value;
    const addressData = JSON.parse(selectedOption);
    console.log('updating manual fields')
    document.getElementById('address_line1').value = addressData.AddressLine1 || '';
    document.getElementById('address_line2').value = addressData.AddressLine2 || '';
    document.getElementById('address_line3').value = addressData.AddressLine3 || '';
    document.getElementById('town').value = addressData.Town || '';
    document.getElementById('postcode').value = addressData.Postcode || '';
}

// Load the new address candidates from postcode when user presses the button
function loadCandidates() {
    console.log('Loading candidates pydantic');
    const postcode = document.getElementById('postcode').value;
    fetch(`/get_candidatesp?postcode=${postcode}`)
        .then(response => response.json())
        .then(data => {
            const addressSelect = document.getElementById('address-select');
            addressSelect.innerHTML = '';
            data.forEach(addressChoice => {
                console.log('addr chouce', addressChoice)
                const option = document.createElement('option');
                option.value = JSON.stringify(addressChoice.Address);
                option.textContent = addressChoice.Address.AddressLine1;
                addressSelect.appendChild(option);
            });
            updateManualFields();
        });
}

// hide the returned request div on page load to avoid resubmission of confirmation
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('main-form');
    const returnedRequestDiv = document.querySelector('.returned-request');
    form.addEventListener('input', function () {
        returnedRequestDiv.style.display = 'none';
    });
    form.addEventListener('submit', function (event) {
        returnedRequestDiv.style.display = '';
    });
});
