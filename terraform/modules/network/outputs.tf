output "nic" {
  value = [azurerm_network_interface.main.id]
}

output "pub_ip" {
  value = azurerm_public_ip.main.ip_address
}

output "vnet_id" {
  value = azurerm_virtual_network.main.id
}

output "vnet_name" {
  value = azurerm_virtual_network.main.name
}
