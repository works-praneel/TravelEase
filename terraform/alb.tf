resource "aws_lb" "app_lb" {
  name               = "TravelEase-ALB"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = [
    aws_subnet.public_subnet_1.id,
    aws_subnet.public_subnet_2.id
  ]

  tags = {
    Name = "TravelEaseALB"
  }
}

# --- Booking Service Target Group ---
resource "aws_lb_target_group" "booking_tg" {
  name         = "booking-tg"
  port         = 5000 # Container port for Booking
  protocol     = "HTTP"
  vpc_id       = aws_vpc.main.id
  target_type  = "ip"

  health_check {
    path                = "/ping" # Health check path for Booking (as /ping is reserved for it)
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name = "TravelEaseBookingTG"
  }
}

# --- Payment Service Target Group ---
resource "aws_lb_target_group" "payment_tg" {
  name         = "payment-tg"
  port         = 5003 # Container port for Payment
  protocol     = "HTTP"
  vpc_id       = aws_vpc.main.id
  target_type  = "ip"

  health_check {
    path                = "/" # Health check path for Payment (checking the root path)
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name = "TravelEasePaymentTG"
  }
}

# --- Flight Service Target Group ---
resource "aws_lb_target_group" "flight_tg" {
  name         = "flight-tg"
  port         = 5002 # Container port for Flight
  protocol     = "HTTP"
  vpc_id       = aws_vpc.main.id
  target_type  = "ip"

  health_check {
    path                = "/" # Health check path for Flight (checking the root path)
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name = "TravelEaseFlightTG"
  }
}

# --- ALB Listener (HTTP on port 80) ---
resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = 80
  protocol          = "HTTP"

  # Default action: Forward all unmatched traffic to the Booking service
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.booking_tg.arn
  }

  tags = {
    Name = "TravelEase-HTTP-Listener"
  }
}

# --- ALB Listener Rule for Payment Service ---
resource "aws_lb_listener_rule" "payment_rule" {
  listener_arn = aws_lb_listener.http_listener.arn
  priority     = 10 # Lower priority means it's evaluated first

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.payment_tg.arn
  }

  condition {
    path_pattern {
      # Matches /pay, /payment, /api/payment and their subpaths
      values = ["/pay*", "/payment*", "/api/payment*"]
    }
  }
}

# --- ALB Listener Rule for Flight Service ---
resource "aws_lb_listener_rule" "flight_rule" {
  listener_arn = aws_lb_listener.http_listener.arn
  priority     = 20 # Higher priority than payment_rule

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.flight_tg.arn
  }

  condition {
    path_pattern {
      # Matches /flight, /flight/search, /flight/api/search, etc.
      values = ["/flight*", "/flight/search*", "/flight/api/search*"]
    }
  }
}

# --- ALB Listener Rule for Booking Service (Explicit Rule) ---
# This rule will be evaluated before the default action.
resource "aws_lb_listener_rule" "booking_rule" {
  listener_arn = aws_lb_listener.http_listener.arn
  priority     = 30 # A higher priority than Flight and Payment rules

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.booking_tg.arn
  }

  condition {
    path_pattern {
      values = ["/booking*", "/booking/ping*"] # Matches /booking and /booking/ping and any subpaths
    }
  }
}
