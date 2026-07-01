terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

data "docker_network" "cicd" {
  name = "cicd-network"
}

resource "docker_image" "minilink" {
  name         = "minilink-api:${var.image_tag}"
  keep_locally = true
}

resource "docker_container" "minilink_staging" {
  name    = var.container_name
  image   = docker_image.minilink.image_id
  restart = "unless-stopped"

  networks_advanced {
    name = data.docker_network.cicd.name
  }

  ports {
    internal = 8000
    external = var.app_port
  }

  env = ["ENV=staging", "LOG_LEVEL=INFO"]

  healthcheck {
    test     = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health')\""]
    interval = "30s"
    timeout  = "10s"
    retries  = 3
  }
}
