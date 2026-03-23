variable "project" {
  default = "tropmed"
}

variable "env" {
  type = string
}

variable "aws_region" {
  default = "us-east-1"
}

variable "backend_image" {
  type = string
}
