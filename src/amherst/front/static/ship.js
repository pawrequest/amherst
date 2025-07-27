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
 // * @param {ShipmentSnake} shipment - The shipment data in snake_case.
 */
function populateShipmentSnake(shipment) {
    console.log('Populating form from shipment');

    document.getElementById('ship_date').value = shipment.shipping_date;
    document.getElementById('boxes').value = shipment.total_number_of_parcels || 1;
    document.getElementById('business_name').value = shipment.recipient_contact.business_name || "";
    document.getElementById('contact_name').value = shipment.recipient_contact.contact_name || "";
    document.getElementById('email').value = shipment.recipient_contact.email_address || "";
    document.getElementById('mobile_phone').value = shipment.recipient_contact.mobile_phone || "";
    document.getElementById('reference_number1').value = shipment.reference_number1 || "";
    document.getElementById('reference_number2').value = shipment.reference_number2 || "";
    document.getElementById('reference_number3').value = shipment.reference_number3 || "";
    document.getElementById('special_instructions1').value = shipment.special_instructions1 || "";
    document.getElementById('special_instructions2').value = shipment.special_instructions2 || "";
    document.getElementById('special_instructions3').value = shipment.special_instructions3 || "";
    document.getElementById('address_line1').value = shipment.recipient_address.address_line1 || "";
    document.getElementById('address_line2').value = shipment.recipient_address.address_line2 || "";
    document.getElementById('address_line3').value = shipment.recipient_address.address_line3 || "";
    document.getElementById('town').value = shipment.recipient_address.town || "";
    document.getElementById('postcode').value = shipment.recipient_address.postcode || "";
}



function toggleOwnLabel() {
    let direction = document.getElementById("direction").value;
    let ownLabel = document.getElementById("own_label");
    if (direction === "in") {
        console.log('Showing own label fields');
        ownLabel.style.opacity = '100';
    } else {
        console.log('Hiding own label fields');
        ownLabel.style.opacity = '0'
    }
}

function updateAddressFromSelect() {
    const selectedOption = document.getElementById('address-select').value;
    updateAddressFieldsFromOption(selectedOption);
}

function updateAddressFieldsFromOption(option) {
    const addressData = JSON.parse(option);
    updateAddressFields(addressData);
}

function updateAddressFields(addressData) {
    console.log('Updating manual fields');
    document.getElementById('address_line1').value = addressData.AddressLine1 || '';
    document.getElementById('address_line2').value = addressData.AddressLine2 || '';
    document.getElementById('address_line3').value = addressData.AddressLine3 || '';
    document.getElementById('town').value = addressData.Town || '';
    document.getElementById('postcode').value = addressData.Postcode || '';
}


async function initShipForm2(shipment) {
    populateShipmentSnake(shipment);
    await loadAddrChoices();
    toggleOwnLabel();
}


async function loadAddrChoices() {
    // get address from form fields
    const address = addressFromInputs();
    // fetch AddressChices from server
    const addrChoicesJson = await fetchAddrChoices(address.Postcode, address);
    // populate address-select options and 'click to insert' div
    await handleAddrChoices(addrChoicesJson);
}

async function fetchAddrChoices(postcode, address) {
    console.log('Fetching AddressChoices at postcode:', postcode, 'matching address:', address);
    try {
        const response = await fetch('/ship/cand', {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({postcode, address})
        });
        return await response.json();
    } catch (error) {
        console.error('Error fetching candidates:', error);
    }
}

function handleAddrChoices(addrChoices) {
    let highestScoreOption = null;
    let highestScore = -Infinity;
    const addressSelect = document.getElementById('address-select');
    addressSelect.innerHTML = '';

    addrChoices.forEach(choice => {
        const option = addrChoiceOption(choice);
        if (choice.Score > highestScore) {
            highestScore = choice.Score;
            highestScoreOption = option;
        }
        addressSelect.appendChild(option);
    });

    if (highestScoreOption) {
        console.log('Match Score', highestScore, '%', highestScoreOption.value);
        highestScoreOption.selected = true;
        setScoreSpan(highestScoreOption);
    }
}

function addrChoiceOption(addressChoice) {
    const option = document.createElement('option');
    option.value = JSON.stringify(addressChoice.Address);
    option.textContent = addressLinesOutput(addressChoice.Address, ', ');
    option.dataset.score = addressChoice.Score.toString();
    return option;
}

function addressLinesOutput(address, seperator) {
    return getAddressLines(address).join(seperator);
}

function getAddressLines(address) {
    return [address.AddressLine1, address.AddressLine2, address.AddressLine3]
        .filter(line => line);
}


function scoreCssSelector(score) {
    if (score > 80) return 'high-score';
    if (score >= 60) return 'medium-score';
    return 'low-score';
}


function setScoreSpan(option) {
    const scoreSpan = document.getElementById('score-span');
    const address = JSON.parse(option.value);
    const score = parseInt(option.dataset.score, 10) || 0;
    const addressHtml = addressLinesOutput(address, '<br>');

    scoreSpan.className = scoreCssSelector(score);
    scoreSpan.innerHTML = `Best Guess (click to insert)<br>${addressHtml}`;
    scoreSpan.onclick = updateAddressFromSelect;
}

function addressFromInputs() {
    return {
        AddressLine1: document.getElementById('address_line1').value,
        AddressLine2: document.getElementById('address_line2').value,
        AddressLine3: document.getElementById('address_line3').value,
        Town: document.getElementById('town').value,
        Postcode: document.getElementById('postcode').value
    };
}


// ************************************

/**
 * Populates form fields with shipment data.
 // * @param {Shipment} shipment - The shipment data.
 */
// function populateShipmentCamel(shipment) {
//     console.log('Populating form from shipment data:', shipment);
//
//     document.getElementById('ship_date').value = shipment.ShippingDate;
//     document.getElementById('boxes').value = shipment.TotalNumberOfParcels || 1;
//     document.getElementById('business_name').value = shipment.RecipientContact.BusinessName || "";
//     document.getElementById('contact_name').value = shipment.RecipientContact.ContactName || "";
//     document.getElementById('email').value = shipment.RecipientContact.EmailAddress || "";
//     document.getElementById('mobile_phone').value = shipment.RecipientContact.MobilePhone || "";
//     document.getElementById('reference_number1').value = shipment.ReferenceNumber1 || "";
//     document.getElementById('reference_number2').value = shipment.ReferenceNumber2 || "";
//     document.getElementById('reference_number3').value = shipment.ReferenceNumber3 || "";
//     document.getElementById('special_instructions1').value = shipment.SpecialInstructions1 || "";
//     document.getElementById('special_instructions2').value = shipment.SpecialInstructions2 || "";
//     document.getElementById('special_instructions3').value = shipment.SpecialInstructions3 || "";
//     document.getElementById('address_line1').value = shipment.RecipientAddress.AddressLine1 || "";
//     document.getElementById('address_line2').value = shipment.RecipientAddress.AddressLine2 || "";
//     document.getElementById('address_line3').value = shipment.RecipientAddress.AddressLine3 || "";
//     document.getElementById('town').value = shipment.RecipientAddress.Town || "";
//     document.getElementById('postcode').value = shipment.RecipientAddress.Postcode || "";
// }


// function handleAddrChoices(addrChoices) {
//     const addressSelect = document.getElementById('address-select');
//     addressSelect.innerHTML = '';
//     let highestScoreOption = null;
//     let highestScore = -Infinity;
//
//     addrChoices.forEach(addressChoice => {
//         const option = document.createElement('option');
//         option.value = JSON.stringify(addressChoice.Address);
//         option.textContent = addressChoice.Address.AddressLine1;
//
//         if (addressChoice.Score > highestScore) {
//             highestScore = addressChoice.Score;
//             highestScoreOption = option;
//         }
//         option.setAttribute('data-score', addressChoice.Score.toString());
//         addressSelect.appendChild(option);
//     });
//     if (highestScoreOption) {
//         console.log('Match Score ', highestScore, '%', highestScoreOption.value);
//         highestScoreOption.selected = true;
//     }
// }
//
// function fetchAddrChoices(postcode, address = null) {
//     console.log('Fetching candidates', address);
//     const requestBody = {
//         postcode: postcode, address: address
//     };
//
//     fetch('/ship/cand', {
//         method: 'POST', headers: {
//             'Content-Type': 'application/json',
//         }, body: JSON.stringify(requestBody)
//     })
//         .then(response => response.json())
//         .then(data => {
//             console.log('Received address candidates:', data);
//             handleAddrChoices(data);
//         })
//         .then(() => {
//             setMatchScoreStyle();
//         })
//         .catch(error => {
//             console.error('Error fetching candidates:', error);
//         });
// }
//
//
// function loadAddrChoices() {
//     const address = {
//         AddressLine1: document.getElementById('address_line1').value,
//         AddressLine2: document.getElementById('address_line2').value,
//         AddressLine3: document.getElementById('address_line3').value,
//         Town: document.getElementById('town').value,
//         Postcode: document.getElementById('postcode').value
//     };
//     fetchAddrChoices(address.postcode, address);
// }
//
// function setMatchScoreStyle() {
//     const scoreSpan = document.getElementById('score-span');
//     const selectedOption = document.getElementById('address-select').selectedOptions[0];
//     const address = JSON.parse(selectedOption.value);
//     const score = selectedOption ? parseInt(selectedOption.getAttribute('data-score'), 10) : 0;
//
//     let address_str = address.AddressLine1
//     if (address.AddressLine2) {
//         address_str += '<br>' + address.AddressLine2;
//     }
//     let newClass;
//
//     if (score > 80) {
//         newClass = 'high-score';
//     } else if (score >= 60 && score <= 80) {
//         newClass = 'medium-score';
//     } else {
//         newClass = 'low-score';
//     }
//     scoreSpan.className = newClass;
//     scoreSpan.innerHTML = `Best Guess (click to insert)<br>${address_str}<br>score=${score}%:`;
//     scoreSpan.onclick = updateAddress;
// }
