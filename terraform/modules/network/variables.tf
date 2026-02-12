# Data

variable "resource_group_name" {
  type = string
}

variable "resource_group_location" {
  type = string
}

# Network variables

variable "address_space" {
  type = string
}

variable "address_prefixes" {
  type = string
}

variable "allowed_ip" {
  type = string
}

# Environment variables

variable "project_name" {
  type = string
}
