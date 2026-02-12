resource "azurerm_virtual_network" "main" {
  name                = "${var.project_name}-vnet"
  resource_group_name = var.resource_group_name
  location            = var.resource_group_location
  address_space       = [var.address_space]
}

resource "azurerm_subnet" "main" {
  name                 = "${var.project_name}-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.address_prefixes]
}

# Public IP

resource "azurerm_public_ip" "main" {
  name                = "${var.project_name}-public-ip"
  resource_group_name = var.resource_group_name
  location            = var.resource_group_location
  allocation_method   = "Static"
}

# NIC

resource "azurerm_network_interface" "main" {
  name                = "${var.project_name}-nic"
  resource_group_name = var.resource_group_name
  location            = var.resource_group_location

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.main.id
  }
}

# NSG

resource "azurerm_network_security_group" "main" {
  name                = "${var.project_name}-nsg"
  resource_group_name = var.resource_group_name
  location            = var.resource_group_location

  security_rule {
    name                       = "AllowSSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.allowed_ip
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "HTTP"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "HTTPS"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 4000
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    project_name = var.project_name
  }
}

resource "azurerm_subnet_network_security_group_association" "main" {
  subnet_id                 = azurerm_subnet.main.id
  network_security_group_id = azurerm_network_security_group.main.id
}
