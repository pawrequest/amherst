/**
 * @typedef {Object} Contact
 * @property {string} ContactName
 * @property {string} EmailAddress
 * @property {string} MobilePhone
 */

/**
 * @typedef {Object} Address
 * @property {string} AddressLine1
 * @property {string} [AddressLine2]
 * @property {string} [AddressLine3]
 * @property {string} Town
 * @property {string} Postcode
 */

/**
 * @typedef {Object} Shipment
 * @property {Address} RecipientAddress
 * @property {Contact} RecipientContact
 * @property {number} TotalNumberOfParcels
 * @property {string} ShippingDate
 * @property {string} BusinessName
 * @property {string} ReferenceNumber1
 * @property {string} ReferenceNumber2
 * @property {string} ReferenceNumber3
 * @property {string} SpecialInstructions1
 * @property {string} SpecialInstructions2
 * @property {string} SpecialInstructions3
 */



function filterRecords() {
    let input = document.getElementById('filterInput');
    let filter = input.value.toLowerCase();
    let recordsContainer = document.querySelector('.record-container');
    let records = recordsContainer.getElementsByClassName('record');

    Array.from(records).forEach(record => {
        if (record.textContent.toLowerCase().includes(filter)) {
            record.style.display = "";
        } else {
            record.style.display = "none";
        }
    });
}


/**
 * Populates form fields with shipment data.
 * @param {Shipment} shipment - The shipment data.
 * @param record
 */
function populateForm(shipment, record) {
    // console log the shipment data
    console.log('Populating form from shipment data:', shipment);
    console.log('Populating form from record data:', record);
    document.getElementById('ship_date').value = shipment.ShippingDate;
    document.getElementById('boxes').value = shipment.TotalNumberOfParcels || 1;
    document.getElementById('business_name').value = shipment.RecipientContact.BusinessName || "";
    document.getElementById('contact_name').value = shipment.RecipientContact.ContactName || "";
    document.getElementById('email').value = shipment.RecipientContact.EmailAddress || "";
    document.getElementById('mobile_phone').value = shipment.RecipientContact.MobilePhone || "";
    document.getElementById('reference_number1').value = shipment.ReferenceNumber1 || "";
    document.getElementById('reference_number2').value = shipment.ReferenceNumber2 || "";
    document.getElementById('reference_number3').value = shipment.ReferenceNumber3 || "";
    document.getElementById('special_instructions1').value = shipment.SpecialInstructions1 || "";
    document.getElementById('special_instructions2').value = shipment.SpecialInstructions2 || "";
    document.getElementById('special_instructions3').value = shipment.SpecialInstructions3 || "";
    document.getElementById('address_line1').value = shipment.RecipientAddress.AddressLine1 || "";
    document.getElementById('address_line2').value = shipment.RecipientAddress.AddressLine2 || "";
    document.getElementById('address_line3').value = shipment.RecipientAddress.AddressLine3 || "";
    document.getElementById('town').value = shipment.RecipientAddress.Town || "";
    document.getElementById('postcode').value = shipment.RecipientAddress.Postcode || "";
    document.getElementById('record').value = record;
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


function loadCandidates() {
    console.log('Loading candidates');
    const postcode = document.getElementById('postcode').value;
    fetch(`/ship/candidates?postcode=${postcode}`)
        .then(response => response.json())
        .then(data => {
            const addressSelect = document.getElementById('address-select');
            addressSelect.innerHTML = '';
            data.forEach(addressChoice => {
                const option = document.createElement('option');
                option.value = JSON.stringify(addressChoice.Address);
                option.textContent = addressChoice.Address.AddressLine1;
                option.setAttribute('data-score', addressChoice.Score);
                addressSelect.appendChild(option);
            });
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

function updateAddress() {
    const selectedOption = document.getElementById('address-select').value;
    const addressData = JSON.parse(selectedOption);
    console.log('Updating manual fields');
    document.getElementById('address_line1').value = addressData.AddressLine1 || '';
    document.getElementById('address_line2').value = addressData.AddressLine2 || '';
    document.getElementById('address_line3').value = addressData.AddressLine3 || '';
    document.getElementById('town').value = addressData.Town || '';
    document.getElementById('postcode').value = addressData.Postcode || '';
}

function initShipPage(shipment, record) {
    toggleOwnLabel();
    populateForm(shipment, record);
    loadCandidates();
}


