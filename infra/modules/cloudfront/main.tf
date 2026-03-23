variable "project" { type = string }
variable "env" { type = string }
variable "s3_bucket" { type = string }

resource "aws_cloudfront_distribution" "main" {
  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name = "${var.s3_bucket}.s3.amazonaws.com"
    origin_id   = "s3-frontend"
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "s3-frontend"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

output "domain_name" { value = aws_cloudfront_distribution.main.domain_name }
