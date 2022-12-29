---
title: "Pre-Requisites"
date: 2022-10-30T23:20:21+01:00
draft: false
tags: ["Self-Hosting"]
---

Self - hosting can be simplified with Docker, thanks to the great work of the community that bundles a lot of services into docker images and make them available with their code.

To install docker in the RPI, we need a different installation since their processors are ARM based.

{{< cmd >}}sudo apt-get update && sudo apt-get upgrade && curl -fsSL https://get.docker.com -o get-docker.sh{{< /cmd >}}

```
sudo sh get-docker.sh && docker version

#Test that docker works with this image:
#sudo docker run hello-world
```

{{< warning >}}
Remember that the RPi works with an ARM processors, so expect some changes in the .yml configuration files when another compatible image has to be used. When pulling the images, docker will find the one that suits your machine (if no specific version is specified) when available.
{{< /warning >}}

{{< gist JAlcocerT 197667ec5ec0da53e78eb58c4253a73f>}}