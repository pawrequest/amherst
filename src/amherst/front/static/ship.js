// async function populateForm(csrname, rowId) {
//         const resp = await fetch(`/api/${csrname}/${rowId}`)
//         const row = await resp.json()
//         document.getElementById('ship_date').value = row.send_date;
//         document.getElementById('boxes').value = row.boxes;
//         document.getElementById('business_name').value = row.delivery_contact_business;
//         document.getElementById('contact_name').value = row.delivery_contact_name;
//         document.getElementById('email').value = row.delivery_contact_email;
//         document.getElementById('mobile_phone').value = row.delivery_contact_phone;
//         document.getElementById('reference_number1').value = row.reference_number1;
//         document.getElementById('reference_number2').value = row.reference_number2;
//         document.getElementById('reference_number3').value = row.reference_number3;
//         document.getElementById('special_instructions1').value = row.special_instructions1;
//         document.getElementById('special_instructions2').value = row.special_instructions2;
//         document.getElementById('special_instructions3').value = row.special_instructions3;
//         document.getElementById('address_line1').value = row.delivery_address_line1;
//         document.getElementById('address_line2').value = row.delivery_address_line2;
//         document.getElementById('address_line3').value = row.delivery_address_line3;
//         document.getElementById('town').value = row.delivery_town;
//         document.getElementById('postcode').value = row.delivery_address_pc;
//     }

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
 * @property {string} ShippingDate
 * @property {number} TotalNumberOfParcels
 * @property {string} BusinessName
 * @property {Contact} RecipientContact
 * @property {string} ReferenceNumber1
 * @property {string} ReferenceNumber2
 * @property {string} ReferenceNumber3
 * @property {string} SpecialInstructions1
 * @property {string} SpecialInstructions2
 * @property {string} SpecialInstructions3
 * @property {Address} RecipientAddress
 */



/**
 * Populates form fields with shipment data.
 * @param {Shipment} shipment - The shipment data.
 */
function populateForm(shipment) {
    // console log the shipment data
    console.log('Populating form from shipment data:', shipment);
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

function initShipPage(shipment) {
        // toggleOwnLabel();
        // setMatchScoreStyle();
        // document.getElementById("direction").addEventListener("change", toggleOwnLabel);
        // let shipment = { shipment|tojson };
        populateForm(shipment);
        loadCandidates();
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
// initShipPage();
// document.addEventListener("DOMContentLoaded", function () {
//     initShipPage();
// });

