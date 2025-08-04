const homePage = document.getElementById('homePage');
const flightServicePage = document.getElementById('flightServicePage');
const bookingServicePage = document.getElementById('bookingServicePage');
const paymentDetailsPage = document.getElementById('paymentDetailsPage');
const bookingConfirmedModal = document.getElementById('bookingConfirmedModal');

// Global state for selected items
let selectedFlight = '';
let selectedFlightPrice = 0; 
let selectedSeatClass = '';
let departureDate = '';
let returnDate = '';
let finalBookingPrice = 0; 

// Service URLs are now dynamically replaced
const API_BASE_URL = '__API_BASE_URL__';
const FLIGHT_SERVICE_URL = API_BASE_URL + '/flight';
const PAYMENT_SERVICE_URL = API_BASE_URL + '/payment';
const BOOKING_SERVICE_URL = API_BASE_URL + '/booking';


// Helper function for INR formatting
function formatINR(amount) {
    if (typeof amount !== 'number' || isNaN(amount)) {
        return '₹N/A';
    }
    return `₹${amount.toLocaleString('en-IN')}`;
}

function showPage(pageToShow) {
    homePage.classList.add('hidden');
    flightServicePage.classList.add('hidden');
    bookingServicePage.classList.add('hidden');
    paymentDetailsPage.classList.add('hidden');
    bookingConfirmedModal.classList.add('hidden');
    
    pageToShow.classList.remove('hidden');
    window.scrollTo(0, 0);
}

document.getElementById('travelEaseLogo').addEventListener('click', () => {
    showPage(homePage);
    clearAllFormData();
});

document.getElementById('searchFlightsBtn').addEventListener('click', async () => {
    departureDate = document.getElementById('departureDate').value;
    returnDate = document.getElementById('returnDate').value;

    if (!departureDate) {
        alert('Please select a departure date.');
        return;
    }

    document.getElementById('displayDepartureDate').textContent = departureDate;
    document.getElementById('displayReturnDate').textContent = returnDate || 'N/A';

    try {
        const response = await fetch(`${FLIGHT_SERVICE_URL}/api/search`); 
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! Status: ${response.status} - ${errorText}`);
        }
        const message = await response.text();
        console.log('Backend message (Flight Search):', message);
    } catch (error) {
        console.error('Error fetching flights:', error);
        alert('Failed to fetch flights. Please ensure the backend service is running and accessible.');
    }

    showPage(flightServicePage);
});

document.querySelectorAll('.select-flight-btn').forEach(button => {
    button.addEventListener('click', (event) => {
        selectedFlight = event.currentTarget.dataset.flightId;
        selectedFlightPrice = parseInt(event.currentTarget.dataset.flightPrice); 
        
        document.getElementById('displaySelectedFlight').textContent = selectedFlight;
        document.getElementById('paymentSelectedFlight').textContent = selectedFlight; 
        
        updateSeatClassPrices();

        showPage(bookingServicePage);
    });
});

document.getElementById('modifySearchBtn').addEventListener('click', () => {
    showPage(homePage);
});

function updateSeatClassPrices() {
    const economyPlusIncrement = 12000;
    const businessClassIncrement = 60000;

    const priceEconomySpan = document.getElementById('priceEconomy');
    const priceEconomyPlusSpan = document.getElementById('priceEconomyPlus');
    const priceBusinessSpan = document.getElementById('priceBusiness');

    if (priceEconomySpan) priceEconomySpan.textContent = formatINR(selectedFlightPrice);
    if (priceEconomyPlusSpan) priceEconomyPlusSpan.textContent = formatINR(selectedFlightPrice + economyPlusIncrement);
    if (priceBusinessSpan) priceBusinessSpan.textContent = formatINR(selectedFlightPrice + businessClassIncrement);

    const economyRadio = document.querySelector('input[name="seatClass"][value="Economy"]');
    if (economyRadio) economyRadio.checked = true;
}

document.getElementById('backToHomeBtn').addEventListener('click', () => {
    showPage(homePage);
});

document.getElementById('proceedToPaymentBtn').addEventListener('click', async () => {
    const selectedSeatRadio = document.querySelector('input[name="seatClass"]:checked');
    if (selectedSeatRadio) {
        selectedSeatClass = selectedSeatRadio.value; 
        const seatClassText = selectedSeatRadio.value.replace(/([A-Z])/g, ' $1').trim();
        
        if (selectedSeatClass === 'Economy') finalBookingPrice = selectedFlightPrice;
        else if (selectedSeatClass === 'EconomyPlus') finalBookingPrice = selectedFlightPrice + 12000;
        else if (selectedSeatClass === 'BusinessClass') finalBookingPrice = selectedFlightPrice + 60000;

        document.getElementById('paymentSelectedSeatClass').textContent = `${seatClassText} Class`; 
        document.getElementById('paymentTotalAmount').textContent = formatINR(finalBookingPrice);

        try {
            const response = await fetch(`${PAYMENT_SERVICE_URL}/api/payment`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ amount: finalBookingPrice, flightId: selectedFlight, seatClass: selectedSeatClass }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! Status: ${response.status} - ${errorText}`);
            }

            const message = await response.text();
            console.log('Backend message (Proceed to Payment):', message);
            showPage(paymentDetailsPage);
        } catch (error) {
            console.error('Error initiating payment:', error);
            alert('Failed to initiate payment. Please ensure the Payment Service is running and accessible.');
        }
    } else {
        alert('Please select a seat class.');
    }
});

document.getElementById('backToFlightsBtn').addEventListener('click', () => {
    showPage(flightServicePage);
});

document.getElementById('paymentForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const bookingData = {
        flightId: selectedFlight,
        seatClass: selectedSeatClass,
        totalAmount: finalBookingPrice,
        fullName: document.getElementById('fullName').value,
        email: document.getElementById('email').value,
        phoneNumber: document.getElementById('phoneNumber').value
    };

    try {
        const response = await fetch(`${BOOKING_SERVICE_URL}/api/book`, {
            method: 'GET',
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! Status: ${response.status} - ${errorText}`);
        }

        const message = await response.text();
        console.log('Backend message (Complete Payment / Booking):', message);
        bookingConfirmedModal.classList.remove('hidden');
    } catch (error) {
        console.error('Error completing booking:', error);
        alert('Booking failed. Please check the console for details and ensure the Booking Service is running.');
    }
});

document.getElementById('backToBookingBtn').addEventListener('click', () => {
    showPage(bookingServicePage);
});

document.getElementById('goToHomeBtn').addEventListener('click', () => {
    bookingConfirmedModal.classList.add('hidden');
    showPage(homePage);
    clearAllFormData();
});

function clearAllFormData() {
    document.getElementById('departureDate').value = '';
    document.getElementById('returnDate').value = '';
    document.getElementById('fullName').value = '';
    document.getElementById('email').value = '';
    document.getElementById('phoneNumber').value = '';
    document.getElementById('cardNumber').value = '';
    document.getElementById('expiryDate').value = '';
    document.getElementById('cvv').value = '';
    
    const economyRadio = document.querySelector('input[name="seatClass"][value="Economy"]'); 
    if (economyRadio) economyRadio.checked = true;
    
    const otherRadios = document.querySelectorAll('input[name="seatClass"]:not([value="Economy"])'); 
    otherRadios.forEach(radio => radio.checked = false);

    selectedFlight = '';
    selectedFlightPrice = 0;
    selectedSeatClass = '';
    departureDate = '';
    returnDate = '';
    finalBookingPrice = 0;
}