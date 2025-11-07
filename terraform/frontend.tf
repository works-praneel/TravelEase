# [File: terraform/frontend.tf] (REPLACE ENTIRE FILE)

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "frontend_bucket" {
  bucket        = "travelease-frontend-ui-${random_id.suffix.hex}"
  force_destroy = true 

  tags = {
    Name = "TravelEaseFrontendBucket"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend_public_access" {
  bucket = aws_s3_bucket.frontend_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "frontend_site" {
  bucket = aws_s3_bucket.frontend_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_policy" "allow_public_access" {
  bucket = aws_s3_bucket.frontend_bucket.id
  depends_on = [aws_s3_bucket_public_access_block.frontend_public_access]

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Sid: "PublicReadGetObject",
      Effect: "Allow",
      Principal: "*",
      Action: "s3:GetObject",
      Resource: "${aws_s3_bucket.frontend_bucket.arn}/*"
    }]
  })
}

# --- FIXED SECTION ---
# Upload all necessary frontend files

resource "aws_s3_object" "index_html" {
  bucket       = aws_s3_bucket.frontend_bucket.id
  key          = "index.html"
  source       = "${path.module}/../index.html" # Path from terraform dir to root
  etag         = filemd5("${path.module}/../index.html")
  content_type = "text/html"
}

resource "aws_s3_object" "crowdpulse_widget" {
  bucket       = aws_s3_bucket.frontend_bucket.id
  key          = "crowdpulse_widget.html"
  source       = "${path.module}/../CrowdPulse/frontend/crowdpulse_widget.html"
  etag         = filemd5("${path.module}/../CrowdPulse/frontend/crowdpulse_widget.html")
  content_type = "text/html"
}

resource "aws_s3_object" "logo" {
  bucket       = aws_s3_bucket.frontend_bucket.id
  key          = "images/travelease_logo.png" # Preserve the path in S3
  source       = "${path.module}/../images/travelease_logo.png"
  etag         = filemd5("${path.module}/../images/travelease_logo.png")
  content_type = "image/png"
}