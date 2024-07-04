async function populateForm(rowId) {
        const resp = await fetch(`/api/get_amrec/${rowId}`)
        const amherst_table = await resp.json()
        document.getElementById('ship_date').value = amherst_table.send_date;
        document.getElementById('boxes').value = amherst_table.boxes;
        document.getElementById('business_name').value = amherst_table.delivery_contact_business;
        document.getElementById('contact_name').value = amherst_table.delivery_contact_name;
        document.getElementById('email').value = amherst_table.delivery_contact_email;
        document.getElementById('mobile_phone').value = amherst_table.delivery_contact_phone;
        document.getElementById('reference_number1').value = amherst_table.reference_number1;
        document.getElementById('reference_number2').value = amherst_table.reference_number2;
        document.getElementById('reference_number3').value = amherst_table.reference_number3;
        document.getElementById('special_instructions1').value = amherst_table.special_instructions1;
        document.getElementById('special_instructions2').value = amherst_table.special_instructions2;
        document.getElementById('special_instructions3').value = amherst_table.special_instructions3;
        document.getElementById('address_line1').value = amherst_table.delivery_address_line1;
        document.getElementById('address_line2').value = amherst_table.delivery_address_line2;
        document.getElementById('address_line3').value = amherst_table.delivery_address_line3;
        document.getElementById('town').value = amherst_table.delivery_town;
        document.getElementById('postcode').value = amherst_table.delivery_address_pc;
    }
function toggleOwnLabel() {
    let direction = document.getElementById("direction").value;
    let ownLabelLabel = document.getElementById("own_label_label");
    let ownLabelSelect = document.getElementById("own_label");
    if (direction === "in") {
        ownLabelLabel.style.display = '';
        ownLabelSelect.style.display = '';
    } else {
        ownLabelLabel.style.display = 'none';
        ownLabelSelect.style.display = 'none';
    }
}

function initShipPage() {
    document.addEventListener("DOMContentLoaded", function () {
        toggleOwnLabel();
        setMatchScoreStyle();
        document.getElementById("direction").addEventListener("change", toggleOwnLabel);
    });
}

function updateManualFields() {
    const selectedOption = document.getElementById('address-select').value;
    const addressData = JSON.parse(selectedOption);
    console.log('Updating manual fields');
    document.getElementById('address_line1').value = addressData.AddressLine1 || '';
    document.getElementById('address_line2').value = addressData.AddressLine2 || '';
    document.getElementById('address_line3').value = addressData.AddressLine3 || '';
    document.getElementById('town').value = addressData.Town || '';
    document.getElementById('postcode').value = addressData.Postcode || '';
}

function loadCandidates() {
    console.log('Loading candidates');
    const postcode = document.getElementById('postcode').value;
    fetch(`/api/candidates?postcode=${postcode}`)
        .then(response => response.json())
        .then(data => {
            const addressSelect = document.getElementById('address-select');
            addressSelect.innerHTML = '';
            data.forEach(addressChoice => {
                const option = document.createElement('option');
                option.value = JSON.stringify(addressChoice.Address);
                option.textContent = addressChoice.Address.AddressLine1;
                addressSelect.appendChild(option);
            });
            updateManualFields();
            setMatchScoreStyle();
        });
}

function setMatchScoreStyle() {
    const scoreSpan = document.getElementById('score-span');
    const selectedOption = document.getElementById('address-select').selectedOptions[0];
    let score = selectedOption ? parseInt(selectedOption.getAttribute('data-score'), 10) : 0;
    let newClass;

    if (score > 80) {
        newClass = 'high-score';
    } else if (score >= 60 && score <= 80) {
        newClass = 'medium-score';
    } else {
        newClass = 'low-score';
    }

    scoreSpan.className = newClass;
    scoreSpan.textContent = `Match Confidence ${score}%:`;
}
