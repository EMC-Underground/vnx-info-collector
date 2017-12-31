# vnx-info-collector

docker build -t vnx-collector .

docker run -e "ARRAY_IP=10.10.10.10" -e "USERNAME=sysadmin" -e "PASSWORD=sysadmin" -e "TARGET_API_URL=http://localhost" -e "LOG_LEVEL=DEBUG" vnx-collector
