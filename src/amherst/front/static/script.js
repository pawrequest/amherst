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

function initPage() {
    document.addEventListener("DOMContentLoaded", function () {
        toggleOwnLabel();
        setMatchScoreStyle();
        document.getElementById("direction").addEventListener("change", toggleOwnLabel);
    });
}

function filterRecords() {
    let input = document.getElementById('searchInput');
    let filter = input.value.toLowerCase();
    let recordsContainer = document.getElementById('recordsContainer');
    let records = recordsContainer.getElementsByClassName('record');

    for (let i = 0; i < records.length; i++) {
        let record = records[i];
        if (record.textContent.toLowerCase().indexOf(filter) > -1) {
            record.style.display = "";
        } else {
            record.style.display = "none";
        }
    }
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

initPage();