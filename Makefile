up_dev_env:
	docker run -d --name="home-assistant" -v ./ha_config:/config -e "TZ=Europe/Moscow" -p 8123:8123 homeassistant/home-assistant
# 	docker run --init -d --restart=unless-stopped --name="home-assistant" -e "TZ=Europe/Moscow" -v ./ha_config:/config -p 8123:8123 homeassistant/home-assistant:latest

down_dev_env:
	docker-compose -f docker-compose.yml -p home-assistant down --volumes --rmi all
