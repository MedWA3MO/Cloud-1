Got it — here’s a **clean, human, non-AI-sounding README**.
No emojis, no hype language, written the way a real developer would explain the project to another developer who found it via Google.

You can copy-paste this directly as `README.md`.

---

# Cloud-1 — WordPress Infrastructure as Code

This repository contains an Infrastructure as Code implementation for deploying a WordPress website in a production-like environment.
It was built as part of the **42 Network Cloud-1 project** and focuses on automation, security, and reproducibility.

The goal is to be able to deploy the same working website on any clean server using automated tools, without manual configuration.

---

## Project Overview

The project deploys a WordPress website using:

* Docker and Docker Compose for containerization
* Ansible for automated provisioning and deployment
* A modular architecture separating concerns (web server, application, database)
* Persistent storage for application data

The deployment is designed to be **idempotent**: running the same automation multiple times produces the same result.

---

## Main Features

* Automated deployment from a fresh server
* Infrastructure defined as code and versioned
* Separate containers for each service
* Persistent volumes for WordPress data
* Basic web security rules applied by default
* No hard-coded secrets in the repository
* Services can be started, stopped, or redeployed independently

---

## Architecture

The infrastructure follows a simple and clear separation of responsibilities:

* Web server container (HTTP/HTTPS entry point)
* PHP / WordPress runtime container
* Database container (local access only)
* Docker volumes for persistent storage
* Ansible roles to provision and configure each part

Only ports **80 and 443** are exposed publicly.
The database is not accessible from outside the host.

---

## Technologies Used

* Docker
* Docker Compose
* Ansible
* WordPress
* Linux (Ubuntu)
* Nginx, PHP, MySQL / MariaDB

---

## Deployment

The deployment is handled through Ansible and Docker.

High-level steps:

1. Provision the server using Ansible
2. Install required dependencies (Docker, Docker Compose)
3. Configure services using Ansible roles
4. Launch containers using Docker Compose
5. Access the WordPress site through the configured domain or IP

Running the deployment multiple times should not break or duplicate resources.

---

## Security Considerations

* Only required ports are exposed
* Database is bound to local interfaces
* Secrets are injected via environment variables
* No credentials are committed to the repository

Additional security measures can be added depending on the target environment.

---

## Purpose

This project was created for educational purposes as part of the 42 curriculum, but it follows real-world DevOps practices.
It is suitable as a reference for:

* Infrastructure as Code concepts
* Basic container orchestration
* Automated WordPress deployments
* Secure service separation

---

## License

This project is provided as-is for learning and demonstration purposes.


