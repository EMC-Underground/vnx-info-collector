# vnx-info-collector

docker build -t vnx-collector .

docker run -e "ARRAY_IP=10.10.10.10" -e "USERNAME=sysadmin" -e "PASSWORD=sysadmin" -e "TARGET_API_URL=http://localhost" -e "LOG_LEVEL=DEBUG" vnx-collector

LOG_LEVEL is optional and defaults to info if not specified

To run this as a one shot in a docker swarm (create service, run container, rm service)

https://github.com/alexellis/jaas

jaas -rm --env ARRAY_IP=10.10.10.10 --env USERNAME=sysadmin --env PASSWORD=sysadmin --env TARGET_API_URL=http://localhost --env LOG_LEVEL=DEBUG -image vnx-collector
