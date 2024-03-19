---
title: Deploying Kubernetes in SBCs - K3s
author: JAlcocerT
date: 2024-01-01 00:10:00 +0800
categories: [IoT & Data Analytics]
tags: [Sensors,Python,MongoDB]
# image:
#   path: /img/metabase.png
#   alt: IoT Project with Python, MongoDB, DHT11/22 sensors and Metabase.
render_with_liquid: false
---

Kubernetes - A tool to manage and automate automated workflows in the cloud. It orchestrates the infrastructure to accomodate the changes in workload.

The developer just need to define a yml with the desired state of your K8s cluster.

In this project we will be collecting **Temperature and Humidity Data** from a DHT11 or a DHT22 Sensor working together with a Raspberry Pi.

The data store will be in MongoDB, which will live in a Docker container.

Rancher is an open source container management platform built for organizations that deploy containers in production. Rancher makes it easy to run Kubernetes everywhere, meet IT requirements, and empower DevOps teams.

## Rancher: k3s

Setting up a High-availability K3s Kubernetes Cluster for Rancher.

We just need to [have Docker installed](https://jalcocert.github.io/RPi/posts/selfhosting-with-docker/) and thanks to Rancher we can **run our own Kubernetes Cluster**.

* <https://hub.docker.com/r/rancher/k3s/tags>
* <https://github.com/rancher/rancher>
* <https://www.rancher.com/community>

### Master Node



```yml
version: '3'
services:
  k3s:
    image: rancher/k3s
    container_name: k3s
    privileged: true
    volumes:
      - k3s-server:/var/lib/rancher/k3s
    ports:
      - "6443:6443"
    restart: unless-stopped

volumes:
  k3s-server:

#docker run -d --name k3s --privileged rancher/k3s  

```


## Using kubectl

**kubectl** is a command-line tool that allows you to run commands against Kubernetes clusters.

It is the primary tool for interacting with and managing Kubernetes clusters, providing a versatile way to handle all aspects of cluster operations.

Common kubectl Commands
kubectl get pods: Lists all pods in the current namespace.
kubectl create -f <filename>: Creates a resource specified in a YAML or JSON file.
kubectl apply -f <filename>: Applies changes to a resource from a file.
kubectl delete -f <filename>: Deletes a resource specified in a file.
kubectl describe <resource> <name>: Shows detailed information about a specific resource.
kubectl logs <pod_name>: Retrieves logs from a specific pod.
kubectl exec -it <pod_name> -- /bin/bash: Executes a command, like opening a bash shell, in a specific container of a pod.

### Slaves


## FAQ

### What are K8s PODs?

### Master and Nodes with Differente CPU archs?

### Rancher Alternatives

* 
*

### What is it Kubeflow?

*  Kubeflow is the machine learning toolkit for Kubernetes:
    * <https://www.kubeflow.org/>
    * <https://github.com/kubeflow/examples>

Kubeflow is an **open-source platform for machine learning and MLOps on Kubernetes**.

It was introduced by Google in 2017 and has since grown to include many other contributors and projects. 

Kubeflow aims to make deployments of machine learning workflows on Kubernetes simple, portable and scalable3. Kubeflow offers services for creating and managing Jupyter notebooks, TensorFlow training, model serving, and pipelines across different frameworks and infrastructures3.

Purpose: Kubeflow is an open-source project designed to make deployments of machine learning (ML) workflows on Kubernetes easier, scalable, and more flexible.

Scope: It encompasses a broader range of ML lifecycle stages, including preparing data, training models, serving models, and managing workflows.

Kubernetes-Based: It’s specifically built for Kubernetes, leveraging its capabilities for managing complex, distributed systems.

Components: Kubeflow includes various components like Pipelines, Katib for hyperparameter tuning, KFServing for model serving, and integration with Jupyter notebooks.

Target Users: It's more suitable for organizations and teams looking to deploy and manage ML workloads at scale in a Kubernetes environment.

### What it is MLFlow?

* <https://mlflow.org/>
* <https://github.com/mlflow/mlflow>

Purpose: MLflow is an open-source platform primarily for managing the end-to-end machine learning lifecycle, focusing on tracking experiments, packaging code into reproducible runs, and sharing and deploying models.

Scope: It’s more focused on the experiment tracking, model versioning, and serving aspects of the ML lifecycle.

Platform-Agnostic: MLflow is designed to work across various environments and platforms. It's not tied to Kubernetes and can run on any system where Python is supported.

Components: Key components of MLflow include MLflow Tracking, MLflow Projects, MLflow Models, and MLflow Registry.

Target Users: It's suitable for both individual practitioners and teams, facilitating the tracking and sharing of experiments, models, and workflows.

While they serve different purposes, Kubeflow and MLflow can be used together in a larger ML system.

For instance, you might use MLflow to track experiments and manage model versions, and then deploy these models at scale using Kubeflow on a Kubernetes cluster.

Such integration would leverage the strengths of both platforms: MLflow for experiment tracking and Kubeflow for scalable, Kubernetes-based deployment and management of ML workflows.
In summary, while Kubeflow and MLflow are not directly related and serve different aspects of the ML workflow, they can be complementary in a comprehensive ML operations (MLOps) strategy.

### Kustomize

* What It Is: Kustomize is a standalone tool to customize Kubernetes objects through a declarative configuration file. It's also part of kubectl since v1.14.
* Usage in DevOps/MLOps:
* Configuration Management: Manage Kubernetes resource configurations without templating.
* Environment-Specific Adjustments: Customize applications for different environments without altering the base resource definitions.
* Overlay Approach: Overlay different configurations (e.g., patches) over a base configuration, allowing for reusability and simplicity.


### Useful Videos to Learn more about K8s

* <https://www.youtube.com/watch?v=PziYflu8cB8>
* <https://www.youtube.com/watch?v=s_o8dwzRlu4>
* <https://www.youtube.com/watch?v=DCoBcpOA7W4>
* <https://www.youtube.com/watch?v=n-fAf2mte6M>