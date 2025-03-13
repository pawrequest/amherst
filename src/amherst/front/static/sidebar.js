async function fetchCustromes(customer_name) {
    try {
        const response = await fetch('/ship/cand', {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({postcode, address})
        });
        return await response.json();
    } catch (error) {
        console.error('Error fetching candidates:', error);
    }
}