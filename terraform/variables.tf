# Data

variable "resource_group_name" {
  type = string
}

variable "key_vault_name" {
  type = string
}

variable "subscription_id" {
  type = string
}

# VM variables

variable "vm_size" {
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
