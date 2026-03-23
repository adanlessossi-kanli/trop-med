variable "project" { type = string }
variable "env" { type = string }
variable "vpc_id" { type = string }
variable "private_subnets" { type = list(string) }

resource "aws_security_group" "redis" {
  vpc_id = var.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project}-${var.env}"
  subnet_ids = var.private_subnets
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.project}-${var.env}"
  description                = "Redis for ${var.project}"
  node_type                  = "cache.t3.small"
  num_cache_clusters         = 1
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.redis.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
}

output "endpoint" { value = aws_elasticache_replication_group.main.primary_endpoint_address }
