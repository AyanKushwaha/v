variable "domain_name" {
  default = "Default"
}

variable "tenant_name" {
  default = "crewbuddies"
}

variable "user_name" {
  default = "crewbuddies"
}

variable "password" {
  default = "jeppesen_crewbuddies"
}

variable "auth_url" {
  default = "https://gotosp13.osp.jeppesensystems.com:13000/v3"
}

variable "system_name" {
  default = "ib6-sas"
}

variable "image_name" {
  default = "DO-NOT-DELETE-crew-buddies-CentOS-7-x86_64-GenericCloud-1907.qcow2c"
}

variable "flavor" {
  default = "j1.c4r8d15"
}

variable "user" {
  default = "centos"
}

variable "timeouts" {
  type = "map"
  default = {
    "create" = "15m"
    "update" = "15m"
    "delete" = "90s"
  }
}
