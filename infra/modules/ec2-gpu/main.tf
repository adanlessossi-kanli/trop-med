variable "project" { type = string }
variable "env" { type = string }
variable "vpc_id" { type = string }
variable "private_subnets" { type = list(string) }
variable "instance_type" { default = "g5.2xlarge" }

data "aws_ami" "deep_learning" {
  most_recent = true
  owners      = ["amazon"]
  filter { name = "name"; values = ["Deep Learning AMI GPU PyTorch *-Ubuntu-*"] }
}

resource "aws_security_group" "gpu" {
  vpc_id = var.vpc_id
  ingress { from_port = 8080; to_port = 8080; protocol = "tcp"; cidr_blocks = ["10.0.0.0/16"] }
  egress  { from_port = 0; to_port = 0; protocol = "-1"; cidr_blocks = ["0.0.0.0/0"] }
  tags = { Name = "${var.project}-${var.env}-gpu" }
}

resource "aws_instance" "gpu" {
  ami                    = data.aws_ami.deep_learning.id
  instance_type          = var.instance_type
  subnet_id              = var.private_subnets[0]
  vpc_security_group_ids = [aws_security_group.gpu.id]

  root_block_device { volume_size = 100; volume_type = "gp3"; encrypted = true }

  tags = { Name = "${var.project}-${var.env}-gpu-inference" }
}

output "private_ip" { value = aws_instance.gpu.private_ip }
