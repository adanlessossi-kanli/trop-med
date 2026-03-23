variable "project" { type = string }
variable "env" { type = string }

resource "aws_s3_bucket" "files" {
  bucket = "${var.project}-${var.env}-files"
}

resource "aws_s3_bucket_versioning" "files" {
  bucket = aws_s3_bucket.files.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "files" {
  bucket = aws_s3_bucket.files.id
  rule { apply_server_side_encryption_by_default { sse_algorithm = "aws:kms" } }
}

resource "aws_s3_bucket_public_access_block" "files" {
  bucket                  = aws_s3_bucket.files.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "frontend" {
  bucket = "${var.project}-${var.env}-frontend"
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  index_document { suffix = "index.html" }
  error_document { key = "404.html" }
}

output "files_bucket" { value = aws_s3_bucket.files.bucket }
output "frontend_bucket" { value = aws_s3_bucket.frontend.bucket }
output "frontend_bucket_arn" { value = aws_s3_bucket.frontend.arn }
