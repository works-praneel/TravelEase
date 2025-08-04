const express = require('express');
const app = express();
const path = require('path');
const fs = require('fs');
const port = 80;

// Serve a dynamically modified index.html
app.get('/', (req, res) => {
    const filePath = path.join(__dirname, 'public', 'index.html');
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            return res.status(500).send('Error loading page.');
        }
        res.send(data);
    });
});

// Serve a dynamically modified script.js
app.get('/script.js', (req, res) => {
    const filePath = path.join(__dirname, 'public', 'script.js');
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            return res.status(500).send('Error loading script.');
        }
        const updatedScript = data.replace(/__API_BASE_URL__/g, 'http://localhost:3000');
        res.type('application/javascript').send(updatedScript);
    });
});

// All other static files will be served directly
app.use(express.static(path.join(__dirname, 'public')));


// Set up the reverse proxy routes
app.use('/flight', (req, res) => {
    const flightServiceUrl = 'http://flight-service:8086';
    const newUrl = `${flightServiceUrl}${req.originalUrl.replace('/flight', '')}`;
    console.log(`Proxying to: ${newUrl}`);
    res.redirect(newUrl);
});

app.use('/payment', (req, res) => {
    const paymentServiceUrl = 'http://payment-service:8086';
    const newUrl = `${paymentServiceUrl}${req.originalUrl.replace('/payment', '')}`;
    console.log(`Proxying to: ${newUrl}`);
    res.redirect(newUrl);
});

app.use('/booking', (req, res) => {
    const bookingServiceUrl = 'http://booking-service:8086';
    const newUrl = `${bookingServiceUrl}${req.originalUrl.replace('/booking', '')}`;
    console.log(`Proxying to: ${newUrl}`);
    res.redirect(newUrl);
});

app.listen(port, () => {
    console.log(`Frontend service listening at http://localhost:${port}`);
});