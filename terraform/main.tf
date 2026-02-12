terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.1.0"
    }
  }
}

provider "azurerm" {
  features {

  }
  subscription_id = var.subscription_id
}

data "azurerm_resource_group" "main" {
  name = var.resource_group_name
}

data "azurerm_key_vault" "main" {
  name                = var.key_vault_name
  resource_group_name = data.azurerm_resource_group.main.name
}

data "azurerm_key_vault_secret" "ssh" {
  name         = "ssh-public-keys"
  key_vault_id = data.azurerm_key_vault.main.id
}

# Modules

module "compute" {
  source                  = "./modules/compute"
  resource_group_name     = data.azurerm_resource_group.main.name
  resource_group_location = data.azurerm_resource_group.main.location
  vm_size                 = var.vm_size

  project_name   = var.project_name
  ssh_public_key = data.azurerm_key_vault_secret.ssh.value

  # Network
  network_interface_ids = module.network.nic

  depends_on = [module.network]
}

module "network" {
  source                  = "./modules/network"
  resource_group_name     = data.azurerm_resource_group.main.name
  resource_group_location = data.azurerm_resource_group.main.location

  project_name     = var.project_name
  address_space    = var.address_space
  address_prefixes = var.address_prefixes
  allowed_ip       = var.allowed_ip
}
