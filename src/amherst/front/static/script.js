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

