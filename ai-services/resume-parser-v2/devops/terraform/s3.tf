resource "aws_s3_bucket" "resume_storage" {
  bucket = "facultyiq-resume-storage-prod"

  tags = {
    Environment = var.environment
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "s3_encryption" {
  bucket = aws_s3_bucket.resume_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
