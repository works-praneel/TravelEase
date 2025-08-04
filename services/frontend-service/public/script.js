document.addEventListener('DOMContentLoaded', () => {
    let serviceUrls = {};
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            serviceUrls = data;
            console.log("Backend service URLs:", serviceUrls);
        })
        .catch(error => console.error('Error fetching config:', error));

    function fetchService(serviceName, url, resultBoxId) {
        const resultBox = document.getElementById(resultBoxId);
        resultBox.textContent = `Calling ${serviceName}...`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                resultBox.textContent = `Success from ${serviceName}: ${JSON.stringify(data)}`;
            })
            .catch(error => {
                resultBox.textContent = `Error from ${serviceName}: ${error}`;
                console.error(error);
            });
    }

    document.getElementById('flightButton').addEventListener('click', () => {
        fetchService('flight', serviceUrls.flightServiceUrl, 'flightResult');
    });
    document.getElementById('bookingButton').addEventListener('click', () => {
        fetchService('booking', serviceUrls.bookingServiceUrl, 'bookingResult');
    });
    document.getElementById('paymentButton').addEventListener('click', () => {
        fetchService('payment', serviceUrls.paymentServiceUrl, 'paymentResult');
    });
});