TAG=v0.0.1
REGISTRY=footprintai

app-recomsys-build:
	docker build -t ${REGISTRY}/benchmark-recomsys:${TAG} -f app/recomsys/Dockerfile .
app-recomsys-push:
	docker push ${REGISTRY}/benchmark-recomsys:${TAG}

app-recomsys: app-recomsys-build app-recomsys-push
