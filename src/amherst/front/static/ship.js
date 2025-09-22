/**
 * @typedef {Object} AddressChoice
 * @property {Object} Address
 * @property {number} Score
 *
 */


/**
 * @typedef {Object} Contact
 * @property {string} ContactName
 * @property {string} EmailAddress
 * @property {string} MobilePhone
 * @property {string} BusinessName
 */


/**
 * @typedef {Object} Address
 * @property {string[]} AddressLines
 * @property {string} Town
 * @property {string} Postcode
 * @property {string} [Country = 'GB']
 */

/**
 * @typedef {Object} FullContact
 * @property {Contact} Contact
 * @property {Address} Address
 */

/**
 * @typedef {Object} Shipment
 * @property {FullContact} Recipient
 * @property {FullContact | null} [Sender=null]
 * @property {number} Boxes
 * @property {string} ShippingDate
 *
 * @property {string} Reference
 * @property {string} SpecialInstructions1
 * @property {string} SpecialInstructions2
 * @property {string} SpecialInstructions3
 */


/**
 * Populates form fields with shipment data.
 // * @param {Shipment} shipment - The shipment data in snake_case.
 */
function populateShipment(shipment) {
    console.log('Populating form from shipment');

    document.getElementById('ship_date').value = shipment.ShippingDate;
    document.getElementById('boxes').value = shipment.Boxes || 1;
    document.getElementById('reference').value = shipment.Reference || "";
    document.getElementById('business_name').value = shipment.Recipient.Contact.BusinessName || "";
    document.getElementById('contact_name').value = shipment.Recipient.Contact.ContactName || "";
    document.getElementById('email').value = shipment.Recipient.Contact.EmailAddress || "";
    document.getElementById('mobile_phone').value = shipment.Recipient.Contact.MobilePhone || "";
    document.getElementById('address_line1').value = shipment.Recipient.Address.AddressLines[0] || "";
    document.getElementById('address_line2').value = shipment.Recipient.Address.AddressLines[1] || "";
    document.getElementById('address_line3').value = shipment.Recipient.Address.AddressLines[2] || "";
    document.getElementById('town').value = shipment.Recipient.Address.Town || "";
    document.getElementById('postcode').value = shipment.Recipient.Address.Postcode || "";
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
    updateAddressFieldsFromJson(selectedOption);
}

function updateAddressFieldsFromJson(address_json) {
    const address = JSON.parse(address_json);
    updateAddressFields(address);
}

/**
 * Update address fields with given address data.
 * @param {Address} Address
 */
function updateAddressFields(Address) {
    console.log('Updating manual fields');
    document.getElementById('address_line1').value = Address.AddressLines[0] || '';
    document.getElementById('address_line2').value = Address.AddressLines?.[1] || '';
    document.getElementById('address_line3').value = Address.AddressLines?.[2] || '';
    document.getElementById('town').value = Address.Town || '';
    document.getElementById('postcode').value = Address.Postcode || '';
}


/**
 * Initialize the ship form with shipment data.
 * @param {Shipment} shipment - The shipment data.
 */
async function initShipForm(shipment) {
    console.log('Initializing ship form with shipment:', shipment);
    populateShipment(shipment);
    await loadAddrChoices();
    toggleOwnLabel();
}


async function loadAddrChoices() {
    // get address from form fields
    const address = addressFromInputs();
    console.log('Loading AddressChoices for address:', address);
    // fetch AddressChices from server
    const addrChoicesJson = await fetchAddrChoices(address.Postcode, address);
    // populate address-select options and 'click to insert' div
    await handleAddrChoices(addrChoicesJson);
}

/**
 * @typedef {Object} AddrChoice
 * @property {Address} Address
 * @property {Number} Score
 */


/**
 * Get AddressChoices from server.
 * @param {String} Postcode
 * @param {Address} Address - The address to search.
 * @returns {Promise<AddrChoice[]>}
 */
async function fetchAddrChoices(Postcode, Address) {
    console.log('Fetching AddressChoices at postcode:', Postcode, 'matching address:', Address);
    console.log('Posting to /ship/cand', {Postcode, Address});
    const requestBody = {
        postcode: Postcode,
        address: Address
    };
    try {
        const response = await fetch('/ship/cand', {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(requestBody)
        });
        return await response.json();
    } catch (error) {
        console.error('Error fetching candidates:', error);
    }
}

/**
 * Handles AddressChoices from server.
 * @param {AddrChoice[]} addrChoices
 */
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

/**
 * Create an option element for an AddressChoice.
 * @param {AddrChoice} addressChoice
 * @returns {HTMLOptionElement}
 */
function addrChoiceOption(addressChoice) {
    const option = document.createElement('option');
    option.value = JSON.stringify(addressChoice.Address);
    option.textContent = addressLinesOutput(addressChoice.Address, ', ');
    option.dataset.score = addressChoice.Score.toString();
    return option;
}


/**
 * Get AddressChoices from server.
 * @param {Address} Address
 * @param {String} Seperator
 * @returns {String}
 */
function addressLinesOutput(Address, Seperator) {
    return getAddressLines(Address).join(Seperator);
}

/**
 * Get non-empty address lines from Address object.
 * @param {Address} Address
 * @returns {string[]}
 */
function getAddressLines(Address) {
    return [...Address.AddressLines]
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
        AddressLines: [document.getElementById('address_line1').value, document.getElementById('address_line2').value, document.getElementById('address_line3').value].filter(line => line),
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
