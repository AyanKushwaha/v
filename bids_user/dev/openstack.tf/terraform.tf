provider "openstack" {
  domain_name = "${var.domain_name}"
  tenant_name = "${var.tenant_name}"
  user_name = "${var.user_name}"
  password = "${var.password}"
  auth_url = "${var.auth_url}"
  version = "<= 1.17"
}

terraform {
  backend "local" {
    path = ".terraform/backend"
  }
}

resource "openstack_compute_keypair_v2" "keypair" {
  name = "${var.system_name}-keypair"
  public_key = "${file("id_rsa.pub")}"
}

resource "openstack_compute_instance_v2" "crewbuddies" {
  name = "${var.system_name}"
  flavor_name = "${var.flavor}"
  image_name = "${var.image_name}"
  key_pair = "${var.system_name}-keypair"

  security_groups = [
    "rocket_security_group"
  ]

  network {
    name = "public"
  }

  connection {
    type = "ssh"
    user = "${var.user}"
    private_key = "${file("id_rsa")}"
    agent = "false"
  }

  timeouts {
    create = "${var.timeouts["create"]}"
    update = "${var.timeouts["update"]}"
    delete = "${var.timeouts["delete"]}"
  }

  provisioner "file" {
    source = "files/"
    destination = "/tmp"
  }

   provisioner "remote-exec" {
     inline = [
       "echo 'export SELF_NAME=${self.name}'",
       "echo 'export SELF_NAME=${self.name}'                     | sudo tee --append /etc/profile.d/crew-buddies-03-self-name.sh",
       "echo 'export SELF_ACCESS_IP_V4=${self.access_ip_v4}'",
       "echo 'export SELF_ACCESS_IP_V4=${self.access_ip_v4}'     | sudo tee --append /etc/profile.d/crew-buddies-04-self-access-ip-v4.sh",
     ]
   }


  provisioner "remote-exec" {
    scripts = [
      "./scripts/01-install-update.sh",
      "./scripts/02-install-software.sh",
      "./scripts/03-install-docker.sh",
      "./scripts/04-crewportal-application.sh",
      "./scripts/05-dns-fqdn.sh",
      "./scripts/06-cleanup.sh",
    ]
  }
}

output "instance_access_ip_v4" {
  value = "${format("%s -> %s","${openstack_compute_instance_v2.crewbuddies.*.name}","${openstack_compute_instance_v2.crewbuddies.*.access_ip_v4}")}"
}
