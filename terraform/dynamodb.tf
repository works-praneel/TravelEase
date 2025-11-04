# 1. Flights Table
resource "aws_dynamodb_table" "flights_table" {
  name           = "TravelEase-Flights"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "flight_id" # Primary Key

  attribute {
    name = "flight_id"
    type = "S"
  }
<<<<<<< HEAD
=======

>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
  attribute {
    name = "route"
    type = "S"
  }
<<<<<<< HEAD
=======

  # Global Secondary Index (GSI) taaki hum 'route' (e.g., "DEL-BOM") se search kar sakein
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
  global_secondary_index {
    name            = "route-index"
    hash_key        = "route"
    projection_type = "ALL"
  }
<<<<<<< HEAD
  tags = { Name = "${var.project_name}-flights-table" }
=======

  tags = {
    Name = "${var.project_name}-flights-table"
  }
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
}

# 2. Bookings Table
resource "aws_dynamodb_table" "bookings_table" {
  name           = "TravelEase-Bookings"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "booking_reference" # Primary Key

  attribute {
    name = "booking_reference"
    type = "S"
  }
<<<<<<< HEAD
  tags = { Name = "${var.project_name}-bookings-table" }
=======

  tags = {
    Name = "${var.project_name}-bookings-table"
  }
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
}

# 3. Seat Inventory Table
resource "aws_dynamodb_table" "seat_inventory_table" {
  name           = "TravelEase-SeatInventory"
  billing_mode   = "PAY_PER_REQUEST"
<<<<<<< HEAD
  hash_key       = "flight_id"   # Partition Key
  range_key      = "seat_number" # Sort Key
=======
  hash_key       = "flight_id"   # Partition Key (e.g., "IndiGo_2025-12-30")
  range_key      = "seat_number" # Sort Key (e.g., "12A")
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92

  attribute {
    name = "flight_id"
    type = "S"
  }
<<<<<<< HEAD
=======

>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
  attribute {
    name = "seat_number"
    type = "S"
  }
<<<<<<< HEAD
  tags = { Name = "${var.project_name}-seats-table" }
=======

  tags = {
    Name = "${var.project_name}-seats-table"
  }
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
}

# 4. IAM Policy jo ECS Tasks ko in tables ko access karne deti hai
resource "aws_iam_policy" "dynamodb_access_policy" {
  name        = "${var.project_name}-DynamoDB-Access-Policy"
  description = "Allows ECS tasks to access TravelEase DynamoDB tables"

  policy = jsonencode({
<<<<<<< HEAD
    Version = "2012-10-17",
=======
    Version = "2012-10-17"
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem"
        ],
        Resource = [
          aws_dynamodb_table.flights_table.arn,
          aws_dynamodb_table.bookings_table.arn,
          aws_dynamodb_table.seat_inventory_table.arn,
          "${aws_dynamodb_table.flights_table.arn}/index/route-index"
        ]
      }
    ]
  })
<<<<<<< HEAD
}
=======
}
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
