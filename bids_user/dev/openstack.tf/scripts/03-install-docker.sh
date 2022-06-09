#!/usr/bin/env bash
echo '

                  03-install-docker.sh

'

curl -fsSL https://get.docker.com/ | sudo sh
sudo usermod -aG docker $(whoami)

echo 'Autoenable and restart docker'
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl enable docker

export DOCKER_COMPOSE_VERSION=1.25.4
echo "Install docker compose: $DOCKER_COMPOSE_VERSION"
curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o ./docker-compose
chmod +x ./docker-compose
sudo mv -f ./docker-compose /usr/bin/
docker-compose version
