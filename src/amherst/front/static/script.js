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



// document.addEventListener("shipmentFormLoaded", function () {
// });

function closePopup() {
    document.getElementById('popupDetails').style.display = 'none';
}




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
