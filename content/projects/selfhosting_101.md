---
title: "Self-Hosting with RPi and Docker: 101"
date: 2022-10-30T23:20:21+01:00
draft: false
tags: ["Self-Hosting"]
---

# Self-Hosting with Docker

## Install Docker

Self - hosting can be simplified with Docker, thanks to the great work of the community that bundles a lot of services into docker images and make them available with their code.

To install docker in the RPI, we need a different installation since their processors are ARM based.

{{< cmd >}}sudo apt-get update && sudo apt-get upgrade && curl -fsSL https://get.docker.com -o get-docker.sh{{< /cmd >}}

```
sudo sh get-docker.sh && docker version

#Test that docker works with this image:
#sudo docker run hello-world
```

### Install Docker-Compose

```
sudo apt install docker-compose -y
```

Check the version with:

{{< cmd >}}
docker-compose --version
{{< /cmd >}}

#### Installing Portainer


{{< cmd >}}
sudo docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce
{{< /cmd >}}

## Trying a *Containerized* App

{{< warning >}}
Remember that the RPi works with an **ARM processors**, so expect some changes in the .yml configuration files when another compatible image has to be used.

When pulling the images, docker will find the one that suits your machine (if no specific version is specified) when available. But make sure that the Docker image tag that you are pulling supports multi-arch*itecture* and that ARM (32 or 64) is between them.
{{< /warning >}}

{{< gist JAlcocerT a1e51600e3153a400dcd63cf31dd1a63>}}


## **Looking Forward to Self-Host other Apps?

* I have been consolidating a list of docker-compose files to deploy in my Docker repository: <https://github.com/JAlcocerT/Docker>
* Also, I have created detailed guides of some of them in my blog: <https://fossengineer.com/tags/self-hosting/>
