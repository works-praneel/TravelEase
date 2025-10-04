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

resource "aws_s3_object" "frontend_files" {
  for_each = fileset("${path.module}/..", "index.html")

  bucket       = aws_s3_bucket.frontend_bucket.id
  key          = each.value
  source       = "${path.module}/../${each.value}"
  etag         = filemd5("${path.module}/../${each.value}")

  content_type = lookup({
    html = "text/html"
    css  = "text/css"
    js   = "application/javascript"
    json = "application/json"
    png  = "image/png"
    jpg  = "image/jpeg"
    svg  = "image/svg+xml"
  }, lower(split(".", each.value)[length(split(".", each.value)) - 1]), "application/octet-stream")
}

output "frontend_website_url" {
  value = aws_s3_bucket_website_configuration.frontend_site.website_endpoint
}

#