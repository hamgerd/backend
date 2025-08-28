# Hamgerd

[![License](https://img.shields.io/badge/License-AGPL3-blue.svg)](https://opensource.org/license/agpl-v3)

An open-source event planning platform.

## Table of Contents

- [Hamgerd](#hamgerd)
  - [Table of Contents](#table-of-contents)
  - [About The Project](#about-the-project)
  - [Core Technologies](#core-technologies)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
  - [API Reference](#api-reference)
  - [License](#license)

## About The Project

Hamgetd is a powerful, open-source event planning system designed to simplify the organization and management of events. This backend system is built with a robust stack of technologies to ensure scalability, reliability, and ease of use.

## Core Technologies

This project is built with [Django](https://www.djangoproject.com/) as the web framework, [Django REST Framework](https://www.django-rest-framework.org/) for building APIs, [Celery](https://docs.celeryq.dev/en/stable/) for handling asynchronous tasks, [PostgreSQL](https://www.postgresql.org/) as the database, [Redis](https://redis.io/) as the message broker, and [Docker](https://www.docker.com/) for containerization. Additionally, [MinIO](https://min.io/) is used for object storage.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Make sure you have the following tools installed on your system:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/hamgerd/backend
   cd backend
   ```

2. **Build and run the services:**

   ```sh
   make dev
   ```

   This command will build the Docker images and start all the services required for the development environment, including the backend server, worker, database, and message broker.

## Usage

Once the services are up and running, you can access the application at `http://localhost:8000`.

The development server will automatically reload when you make changes to the code.

## API Reference

The API documentation is automatically generated and available at the following endpoints:

- **Swagger UI:** `http://localhost:8000/api/v1/swagger/`

## License

Distributed under the AGPL-3.0 License. See `LICENSE` for more information.
