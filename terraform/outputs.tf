# VM
output "vm_username" {
  value = "adminuser"
}

output "vm_id" {
  value = module.compute.vm_id
}

# Network
output "pub_ip" {
  value = module.network.pub_ip
}

output "pvt_ip" {
  value = module.compute.vm_pvt_ip
}

output "vnet_id" {
  value = module.network.vnet_id
}

output "vnet_name" {
  value = module.network.vnet_name
}

# Environment

output "project_name" {
  value = var.project_name
}
