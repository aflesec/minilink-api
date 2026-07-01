output "container_id" {
  value = docker_container.minilink_staging.id
}

output "app_url" {
  value = "http://localhost:${var.app_port}"
}

output "network_name" {
  value = data.docker_network.cicd.name
}
