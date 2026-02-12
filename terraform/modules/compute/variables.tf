# Data

variable "resource_group_name" {
  type = string
}

variable "resource_group_location" {
  type = string
}

# VM variables

variable "vm_size" {
  type = string
}

variable "network_interface_ids" {
  type = list(string)
}

variable "ssh_public_key" {
  type = string
}

# Environment variables

variable "project_name" {
  type = string
}
