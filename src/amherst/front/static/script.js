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

// /**
//  * @typedef {Object} SearchRequest
//  * @property {string} csrName
//  *
//  */
//
//
// async function searchCommence(searchRequest) {
//     const csrName = searchRequest.csrName;
//
// }

async function loadOrders() {
    let recordsContainer = document.querySelector('.record-container');
    let customer = document.getElementById('searchInput').value;
    console.log('loading Orders For Customer:', customer);
    let res = await customerOrders(customer);
    console.log('RES:', res);
    const hires = res.hires.records;
    const sales = res.sales.records;
    // let hires = await fetchCustomerHires(customer);
    recordsContainer.innerHTML = '';
    hires.forEach(hire => {
        let record = document.createElement('div');
        record.className = 'record';
        record.innerHTML = `
            RECORD HTML
        `;
        recordsContainer.appendChild(record);
    });
}

async function fetchCustomerHires(customer_name) {
    const searchRequest = customerOrdersReq("Hire", customer_name);
    return await fetchResponse(searchRequest, customer_name);
}

async function fetchCustomerSales(customer_name) {
    const searchRequest = customerOrdersReq("Sale", customer_name);
    return await fetchResponse(searchRequest, customer_name);
}

async function customerOrders(customer_name) {
    const hires = await fetchCustomerHires(customer_name);
    const sales = await fetchCustomerSales(customer_name);
    return {hires: hires, sales: sales};
}

async function fetchResponse(searchReq, inputStr) {
    try {
        console.log('Fetching', searchReq.csrname, 'for:', inputStr);
        const response = await fetch('/api', {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(searchReq)
        });
        console.log('Response:', response);
        return await response.json();
    } catch (error) {
        console.error('Error fetching', searchReq.csrname, 'records :', error);
    }
}

function customerNameSearchDict(customer_name) {
    return {"customer_name": customer_name};
}

function customerOrdersReq(csrName, customer_name) {
    console.log('CustomerOrdersReq: csrName:', csrName, 'Customer:', customer_name);
    return {"csrname": csrName, "search_dict": customerNameSearchDict(customer_name)};
}

function delay(fn, ms) {
    console.log('Delaying:', fn, ms);
    let timer = 0
    return function (...args) {
        clearTimeout(timer)
        timer = setTimeout(fn.bind(this, ...args), ms || 0)
    }
}

