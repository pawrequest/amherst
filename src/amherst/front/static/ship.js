/**
 * @typedef {Object} AddressChoice
 * @property {Object} Address
 * @property {number} Score
 *
 */

/**
 * @typedef {Object} address_choice_snake
 * @property {Object} address_snake
 * @property {number} score
 *
 */



/**
 * @typedef {Object} Contact
 * @property {string} ContactName
 * @property {string} EmailAddress
 * @property {string} MobilePhone
 */

/**
 * @typedef {Object} contact_snake
 * @property {string} contact_name
 * @property {string} email_address
 * @property {string} mobile_phone
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
 * @typedef {Object} address_snake
 * @property {string} address_line1
 * @property {string} [address_line2]
 * @property {string} [address_line3]
 * @property {string} town
 * @property {string} postcode
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


/**
 * @typedef {Object} shipment_snake
 * @property {Address} recipient_address
 * @property {Contact} recipient_contact
 * @property {number} total_number_of_parcels
 * @property {string} shipping_date
 * @property {string} business_name
 * @property {string} reference_number1
 * @property {string} reference_number2
 * @property {string} reference_number3
 * @property {string} special_instructions1
 * @property {string} special_instructions2
 * @property {string} special_instructions3
 */


/**
 * Populates form fields with shipment data.
 // * @param {Shipment} shipment - The shipment data.
 */
function populateShipment(shipment) {
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


/**
 * Populates form fields with shipment data.
 // * @param {ShipmentSnake} shipment - The shipment data.
 */
function populateShipmentSnake(shipment) {
    console.log('Populating form from shipment data:', shipment);

    document.getElementById('ship_date').value = shipment.shipping_date;
    document.getElementById('boxes').value = shipment.total_number_of_parcels || 1;
    document.getElementById('business_name').value = shipment.recipient_contact.business_name || "";
    document.getElementById('contact_name').value = shipment.recipient_contact.contact_name || "";
    document.getElementById('email').value = shipment.recipient_contact.email_address || "";
    document.getElementById('mobile_phone').value = shipment.recipient_contact.mobile_phone || "";
    document.getElementById('reference_number1').value = shipment.reference_number1 || "";
    document.getElementById('reference_number2').value = shipment.reference_number2 || "";
    document.getElementById('reference_number3').value = shipment.reference_number3 || "";
    document.getElementById('special_instructions1').value = shipment.special_instructions1|| "";
    document.getElementById('special_instructions2').value = shipment.special_instructions2 || "";
    document.getElementById('special_instructions3').value = shipment.special_instructions3 || "";
    document.getElementById('address_line1').value = shipment.recipient_address.address_line1 || "";
    document.getElementById('address_line2').value = shipment.recipient_address.address_line2 || "";
    document.getElementById('address_line3').value = shipment.recipient_address.address_line3 || "";
    document.getElementById('town').value = shipment.recipient_address.town || "";
    document.getElementById('postcode').value = shipment.recipient_address.postcode || "";
}

function populateRecord(record) {
    console.log('Populating form from record data:', record);
    document.getElementById('record_str').value = JSON.stringify(record);
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


function handle_candidates(data) {
    const addressSelect = document.getElementById('address-select');
    addressSelect.innerHTML = '';
    let highestScoreOption = null;
    let highestScore = -Infinity;


    data.forEach(addressChoice => {
        const option = document.createElement('option');
        option.value = JSON.stringify(addressChoice.Address);
        option.textContent = addressChoice.Address.AddressLine1;

        if (addressChoice.Score > highestScore) {
            highestScore = addressChoice.Score;
            highestScoreOption = option;
        }
        option.setAttribute('data-score', addressChoice.Score.toString());
        addressSelect.appendChild(option);
    });
    if (highestScoreOption) {
        console.log('Match Score ', highestScore, '%', highestScoreOption.value);
        highestScoreOption.selected = true;
    }
}


function loadCandidates() {
    const postcode = document.getElementById('postcode').value;
    const address = {
        AddressLine1: document.getElementById('address_line1').value,
        AddressLine2: document.getElementById('address_line2').value,
        AddressLine3: document.getElementById('address_line3').value,
        Town: document.getElementById('town').value,
        Postcode: postcode
    }
    console.log('Loading candidates', address);
    const requestBody = {
        postcode: postcode, address: address
    };

    fetch('/ship/cand', {
        method: 'POST', headers: {
            'Content-Type': 'application/json',
        }, body: JSON.stringify(requestBody)
    })
        .then(response => response.json())
        .then(data => {
            console.log('Received address candidates:', data);
            handle_candidates(data);
        })
        .then(() => {
            setMatchScoreStyle();
        })
        .catch(error => {
            console.error('Error fetching candidates:', error);
        });
}

function setMatchScoreStyle() {
    const scoreSpan = document.getElementById('score-span');
    const selectedOption = document.getElementById('address-select').selectedOptions[0];
    const address = JSON.parse(selectedOption.value);
    const score = selectedOption ? parseInt(selectedOption.getAttribute('data-score'), 10) : 0;

    let address_str = address.AddressLine1
    if (address.AddressLine2) {
        address_str += '<br>' + address.AddressLine2;
    }
    let newClass;

    if (score > 80) {
        newClass = 'high-score';
    } else if (score >= 60 && score <= 80) {
        newClass = 'medium-score';
    } else {
        newClass = 'low-score';
    }

    scoreSpan.className = newClass;
    // scoreSpan.textContent = `Click to insert selected Address ${address_str} Match Confidence ${score}%:`;

    scoreSpan.innerHTML = `Best Guess (click to insert)<br>${address_str}<br>score=${score}%:`;

    scoreSpan.onclick = updateAddress;
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


function initShipPage(shipment) {
    populateShipment(shipment);
    // populateRecord(record);
    toggleOwnLabel();
    loadCandidates();
}



function initSnake(shipment) {
    populateShipmentSnake(shipment);
    // populateRecord(record);
    toggleOwnLabel();
    loadCandidates();
}


