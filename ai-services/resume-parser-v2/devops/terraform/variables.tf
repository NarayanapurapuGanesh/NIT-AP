variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "environment" {
  type    = string
  default = "production"
}

variable "cluster_name" {
  type    = string
  default = "facultyiq-eks-prod"
}
