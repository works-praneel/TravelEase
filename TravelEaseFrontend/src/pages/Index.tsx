import { useState } from 'react';
import { Calendar, Plane, MapPin, CreditCard, CheckCircle, ArrowRight, Star, Users, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';

interface Flight {
  id: string;
  name: string;
  route: string;
  departure: string;
  arrival: string;
  price: number; // Price in INR
  duration: string;
  stops: string;
}

interface SeatClass {
  id: string;
  name: string;
  price: number; // Additional price for seat class in INR
  features: string[];
}

const TravelEase = () => {
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedDates, setSelectedDates] = useState({ departure: '', return: '' });
  const [selectedFlight, setSelectedFlight] = useState<Flight | null>(null);
  const [selectedSeatClass, setSelectedSeatClass] = useState<SeatClass | null>(null);

  // Assuming an approximate conversion rate: 1 USD = 83 INR for demonstration
  // Adjust these prices to your desired INR values
  const flights: Flight[] = [
    {
      id: 'TE101',
      name: 'Flight TE101',
      route: 'Delhi (DEL) → Mumbai (BOM)',
      departure: '08:00 AM',
      arrival: '10:00 AM',
      price: 12450, // Was 150 USD, now 150 * 83 = 12450 INR
      duration: '2h 00m',
      stops: 'Non-stop'
    },
    {
      id: 'TE102',
      name: 'Flight TE102',
      route: 'Delhi (DEL) → Bangalore (BLR)',
      departure: '11:00 AM',
      arrival: '01:30 PM',
      price: 14940, // Was 180 USD, now 180 * 83 = 14940 INR
      duration: '2h 30m',
      stops: 'Non-stop'
    },
    {
      id: 'TE103',
      name: 'Flight TE103',
      route: 'Delhi (DEL) → Chennai (MAA)',
      departure: '03:00 PM',
      arrival: '05:45 PM',
      price: 16600, // Was 200 USD, now 200 * 83 = 16600 INR
      duration: '2h 45m',
      stops: 'Non-stop'
    }
  ];

  // Seat class prices are additional to the base flight price, also converted to INR
  const seatClasses: SeatClass[] = [
    {
      id: 'economy',
      name: 'Economy Class',
      price: 0,
      features: ['Standard seat', 'Meal included', 'Entertainment system']
    },
    {
      id: 'economyPlus',
      name: 'Economy Plus',
      price: 4150, // Was 50 USD, now 50 * 83 = 4150 INR
      features: ['Extra legroom', 'Priority boarding', 'Premium meal', 'Entertainment system']
    },
    {
      id: 'business',
      name: 'Business Class',
      price: 24900, // Was 300 USD, now 300 * 83 = 24900 INR
      features: ['Lie-flat seat', 'Priority check-in', 'Gourmet dining', 'Premium entertainment', 'Lounge access']
    },
    {
      id: 'first',
      name: 'First Class',
      price: 53950, // Was 650 USD, now 650 * 83 = 53950 INR
      features: ['Private suite', 'Personal butler', 'Fine dining', 'Premium amenities', 'Luxury lounge access']
    }
  ];

  const searchFlights = () => {
    if (!selectedDates.departure) {
      alert('Please select a departure date.');
      return;
    }
    setCurrentPage('flights');
  };

  const selectFlight = (flight: Flight) => {
    setSelectedFlight(flight);
    setCurrentPage('booking');
  };

  const proceedToPayment = (seatClass: string) => {
    const seatClassData = seatClasses.find(sc => sc.id === seatClass);
    if (seatClassData) {
      setSelectedSeatClass(seatClassData);
      setCurrentPage('payment');
    }
  };

  const completePayment = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage('confirmation');
  };

  const HomePage = () => (
    <div className="page-transition">
      {/* Hero Section */}
      <div className="relative h-[60vh] min-h-[500px] overflow-hidden rounded-3xl mb-12 bg-gradient-to-br from-blue-500 to-blue-700">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/70 to-blue-600/50" />
        <div className="relative h-full flex items-center justify-center text-center text-white px-8">
          <div className="max-w-4xl animate-fade-in">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-slide-in-bottom">
              TravelEase
            </h1>
            <p className="text-xl md:text-2xl mb-8 opacity-90 animate-slide-in-bottom">
              Your Journey Starts Here - Effortless Flight Booking & Secure Payments
            </p>
            <div className="flex items-center justify-center gap-6 text-sm animate-slide-in-bottom">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                <span>Secure Payments</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="w-5 h-5" />
                <span>Best Prices</span>
              </div>
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                <span>24/7 Support</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search Section */}
      <Card className="travel-card p-8 mb-12 animate-scale-in">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">Find Your Perfect Flight</h2>
          <p className="text-muted-foreground">Choose your dates and discover amazing destinations</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto mb-8">
          <div className="space-y-2">
            <Label htmlFor="departure" className="text-sm font-semibold flex items-center gap-2">
              <Calendar className="w-4 h-4 text-primary" />
              Departure Date
            </Label>
            <Input
              id="departure"
              type="date"
              className="travel-input"
              value={selectedDates.departure}
              onChange={(e) => setSelectedDates(prev => ({ ...prev, departure: e.target.value }))}
              min={new Date().toISOString().split('T')[0]}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="return" className="text-sm font-semibold flex items-center gap-2">
              <Calendar className="w-4 h-4 text-primary" />
              Return Date (Optional)
            </Label>
            <Input
              id="return"
              type="date"
              className="travel-input"
              value={selectedDates.return}
              onChange={(e) => setSelectedDates(prev => ({ ...prev, return: e.target.value }))}
              min={selectedDates.departure || new Date().toISOString().split('T')[0]}
            />
          </div>
        </div>

        <div className="text-center">
          <Button
            onClick={searchFlights}
            className="travel-button-primary text-lg px-8 py-4 animate-pulse-glow"
          >
            <Plane className="w-5 h-5 mr-2" />
            Search Flights
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </Card>

      {/* Featured Destinations */}
      <div className="animate-fade-in">
        <div className="text-center mb-12">
          <h3 className="text-3xl font-bold text-foreground mb-4">Featured Destinations</h3>
          <p className="text-muted-foreground text-lg">Discover amazing places with our specially curated flight offers</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { name: 'New York', price: 24800, description: 'The city that never sleeps', color: 'bg-gradient-to-br from-purple-500 to-blue-600' }, // 299 USD -> 24817 INR, rounded to 24800
            { name: 'Paris', price: 33100, description: 'City of love and lights', color: 'bg-gradient-to-br from-pink-500 to-red-500' }, // 399 USD -> 33117 INR, rounded to 33100
            { name: 'Tokyo', price: 49700, description: 'Modern meets traditional', color: 'bg-gradient-to-br from-cyan-500 to-blue-500' } // 599 USD -> 49717 INR, rounded to 49700
          ].map((destination, index) => (
            <Card key={destination.name} className="destination-card animate-float group" style={{ animationDelay: `${index * 0.2}s` }}>
              <div className={`h-32 rounded-lg mb-4 ${destination.color}`} />
              <h4 className="text-xl font-bold text-primary mb-2 flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                {destination.name}
              </h4>
              <p className="text-muted-foreground text-sm mb-3">{destination.description}</p>
              <div className="flex items-center justify-between">
                <span className="price-highlight">From ₹{destination.price}</span>
                <span className="text-sm text-muted-foreground">Dates vary</span>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );

  const FlightsPage = () => (
    <div className="page-transition">
      <Card className="travel-card p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold text-foreground mb-2">Available Flights</h2>
            <p className="text-muted-foreground">
              {selectedDates.departure} {selectedDates.return && `to ${selectedDates.return}`}
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => setCurrentPage('home')}
            className="travel-button-secondary"
          >
            Modify Search
          </Button>
        </div>

        <div className="space-y-6">
          {flights.map((flight, index) => (
            <Card
              key={flight.id}
              className="flight-card animate-slide-in-bottom"
              style={{ animationDelay: `${index * 0.1}s` }}
              onClick={() => selectFlight(flight)}
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <Plane className="w-5 h-5 text-primary" />
                    <h3 className="text-xl font-bold text-foreground">{flight.name}</h3>
                  </div>
                  <p className="text-muted-foreground mb-2">{flight.route}</p>
                  <div className="flex items-center gap-6 text-sm text-muted-foreground">
                    <span>Departure: {flight.departure}</span>
                    <span>Arrival: {flight.arrival}</span>
                    <span>Duration: {flight.duration}</span>
                    <span className="text-green-600 font-medium">{flight.stops}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="price-highlight mb-2">₹{flight.price}</div>
                  <Button className="travel-button-primary">
                    Select Flight
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </Card>
    </div>
  );

  const BookingPage = () => (
    <div className="page-transition">
      <Card className="travel-card p-8 max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">Select Your Seat Class</h2>
          <p className="text-muted-foreground">
            Selected Flight: <span className="font-semibold text-primary">{selectedFlight?.name}</span> - {selectedFlight?.route}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="space-y-4">
            <RadioGroup onValueChange={proceedToPayment}>
              {seatClasses.map((seatClass, index) => (
                <Label
                  key={seatClass.id}
                  className="seat-option animate-slide-in-bottom flex items-center space-x-3 cursor-pointer"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <RadioGroupItem value={seatClass.id} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-lg font-semibold">{seatClass.name}</span>
                      <span className="price-highlight">
                        ₹{(selectedFlight?.price || 0) + seatClass.price}
                      </span>
                    </div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {seatClass.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center gap-2">
                          <CheckCircle className="w-3 h-3 text-green-500" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </Label>
              ))}
            </RadioGroup>
          </div>

          <div className="animate-scale-in">
            <div className="w-full h-64 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg flex items-center justify-center">
              <div className="text-center text-blue-600">
                <Plane className="w-16 h-16 mx-auto mb-4" />
                <p className="text-lg font-semibold">Airplane Interior</p>
              </div>
            </div>
          </div>
        </div>

        <div className="text-center">
          <Button
            variant="outline"
            onClick={() => setCurrentPage('flights')}
            className="travel-button-secondary mr-4"
          >
            Back to Flights
          </Button>
        </div>
      </Card>
    </div>
  );

  const PaymentPage = () => (
    <div className="page-transition">
      <Card className="travel-card p-8 max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-4">Payment Details</h2>
          <div className="bg-primary/5 rounded-lg p-4 text-left">
            <p className="text-sm text-muted-foreground mb-1">Flight: <span className="font-semibold text-foreground">{selectedFlight?.name}</span></p>
            <p className="text-sm text-muted-foreground mb-1">Seat Class: <span className="font-semibold text-foreground">{selectedSeatClass?.name}</span></p>
            <p className="text-lg font-bold text-primary">Total: ₹{(selectedFlight?.price || 0) + (selectedSeatClass?.price || 0)}</p>
          </div>
        </div>

        <form onSubmit={completePayment} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="fullName">Full Name</Label>
              <Input id="fullName" className="travel-input" placeholder="John Doe" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input id="email" type="email" className="travel-input" placeholder="john@example.com" required />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone">Phone Number</Label>
            <Input id="phone" type="tel" className="travel-input" placeholder="+91 98765 43210" /> {/* Changed placeholder for Indian numbers */}
          </div>

          <div className="border-t pt-6">
            <h3 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-primary" />
              Payment Information
            </h3>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cardNumber">Card Number</Label>
                <Input id="cardNumber" className="travel-input" placeholder="1234 5678 9012 3456" required />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="expiry">Expiry Date</Label>
                  <Input id="expiry" className="travel-input" placeholder="MM/YY" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cvv">CVV</Label>
                  <Input id="cvv" className="travel-input" placeholder="123" required />
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-4 pt-6">
            <Button
              type="button"
              variant="outline"
              onClick={() => setCurrentPage('booking')}
              className="travel-button-secondary flex-1"
            >
              Back to Seat Selection
            </Button>
            <Button type="submit" className="travel-button-primary flex-1 animate-pulse-glow">
              <CreditCard className="w-4 h-4 mr-2" />
              Complete Payment
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );

  const ConfirmationPage = () => (
    <div className="fixed inset-0 bg-background/95 backdrop-blur-sm flex items-center justify-center z-50">
      <Card className="p-8 max-w-md mx-4 text-center animate-scale-in">
        <div className="animate-bounce-subtle">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
        </div>
        <h2 className="text-4xl font-bold text-green-600 mb-4">Booking Confirmed!</h2>
        <p className="text-lg text-muted-foreground mb-6">
          Your flight booking has been successfully processed.
        </p>
        <p className="text-sm text-muted-foreground mb-8">
          A confirmation email has been sent to your provided address.
        </p>
        <Button
          onClick={() => {
            setCurrentPage('home');
            setSelectedFlight(null);
            setSelectedSeatClass(null);
            setSelectedDates({ departure: '', return: '' });
          }}
          className="travel-button-primary w-full"
        >
          Return to Home
        </Button>
      </Card>
    </div>
  );

  const renderPage = () => {
    switch (currentPage) {
      case 'flights': return <FlightsPage />;
      case 'booking': return <BookingPage />;
      case 'payment': return <PaymentPage />;
      case 'confirmation': return <ConfirmationPage />;
      default: return <HomePage />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="header-gradient sticky top-0 z-40 shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div
              className="flex items-center gap-3 cursor-pointer"
              onClick={() => setCurrentPage('home')}
            >
              <Plane className="w-8 h-8 animate-bounce-subtle" />
              <h1 className="text-3xl font-bold">TravelEase</h1>
            </div>
            <nav className="hidden md:flex items-center gap-6">
              <span className="text-sm opacity-90">24/7 Customer Support</span>
              <span className="text-sm opacity-90">Secure Payments</span>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {renderPage()}
      </main>

      {/* Footer */}
      <footer className="bg-foreground text-background py-6 mt-16">
        <div className="container mx-auto px-6 text-center">
          <p>&copy; 2025 TravelEase. All rights reserved. | Secure, Fast, Reliable</p>
        </div>
      </footer>
    </div>
  );
};

export default TravelEase;