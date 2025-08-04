const express = require('express');
const app = express();
const path = require('path');
const port = 80;

app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/config', (req, res) => {
    // In a real setup, this would be dynamically set by Terraform
    // and injected as an environment variable in the ECS task definition.
    // For this example, we'll hardcode the ALB DNS name.
    const backendAlbDns = 'YOUR_ALB_DNS_NAME';
    res.json({
        "paymentServiceUrl": `http://${backendAlbDns}/payment`,
        "bookingServiceUrl": `http://${backendAlbDns}/booking`,
        "flightServiceUrl": `http://${backendAlbDns}/flight`
    });
});

app.listen(port, () => {
    console.log(`Frontend service listening on port ${port}`);
});