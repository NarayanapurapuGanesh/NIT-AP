resource "aws_db_instance" "facultyiq_postgres" {
  allocated_storage      = 50
  engine                 = "postgres"
  engine_version         = "16.1"
  instance_class         = "db.t4g.medium"
  db_name                = "facultyiq"
  username               = "facultyiq_admin"
  password               = "ChangeInVaultSecretKey123"
  multi_az               = true
  skip_final_snapshot    = false
  final_snapshot_identifier = "facultyiq-final-snapshot"
}
