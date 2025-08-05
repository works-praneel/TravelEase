const express = require('express');
const app = express();
const path = require('path');
const fs = require('fs');
const { createProxyMiddleware } = require('http-proxy-middleware');
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


// Set up the reverse proxy for each service
app.use('/flight', createProxyMiddleware({
    target: 'http://travelease-flight-service-1:8086',
    changeOrigin: true,
    pathRewrite: { '^/flight': '' },
    logLevel: 'debug'
}));

app.use('/payment', createProxyMiddleware({
    target: 'http://travelease-payment-service-1:8086',
    changeOrigin: true,
    pathRewrite: { '^/payment': '' },
    logLevel: 'debug'
}));

app.use('/booking', createProxyMiddleware({
    target: 'http://travelease-booking-service-1:8086',
    changeOrigin: true,
    pathRewrite: { '^/booking': '' },
    logLevel: 'debug'
}));

app.listen(port, () => {
    console.log(`Frontend service listening at http://localhost:${port}`);
});