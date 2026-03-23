variable "project" { type = string }
variable "env" { type = string }

resource "aws_secretsmanager_secret" "db_uri" {
  name = "${var.project}/${var.env}/db-uri"
}

resource "aws_secretsmanager_secret" "jwt_secret" {
  name = "${var.project}/${var.env}/jwt-secret"
}

resource "aws_secretsmanager_secret_rotation" "jwt" {
  secret_id = aws_secretsmanager_secret.jwt_secret.id
  rotation_rules { automatically_after_days = 30 }
}
