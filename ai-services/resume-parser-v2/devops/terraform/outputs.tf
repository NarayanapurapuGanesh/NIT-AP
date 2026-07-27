output "eks_cluster_endpoint" {
  value = aws_eks_cluster.facultyiq_cluster.endpoint
}

output "rds_endpoint" {
  value = aws_db_instance.facultyiq_postgres.endpoint
}

output "s3_bucket_name" {
  value = aws_s3_bucket.resume_storage.id
}
