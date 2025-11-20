# Upload API Service

## Description

A secure FastAPI-based service that allows authenticated users to upload and manage ZIP files. The service provides
endpoints for file upload and listing uploaded files, protected by bearer token authentication.

The project includes two services:
- Upload Service: Handles file uploads and management
- Stats Service: Provides statistics and analytics for uploaded files

## Requirements

- Python 3.11 or higher
- FastAPI
- Uvicorn
- Python-multipart
- Docker (optional)
- Docker Compose (optional)

## Setup and Run

### Local Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set the API token (optional):
   ```bash
   export API_BEARER_TOKEN=your_secret_token
   ```
5. Run the application:
   ```bash
   python main.py
   ```
   The service will be available at http://localhost:8000

## Using Docker

### Build and Run with Docker

1. Build the image:
   ```bash
   ./docker-build.sh
   # or
   docker build -t massimocallisto/devops-upload-app:1.0.0 .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 -e API_BEARER_TOKEN=your_secret_token massimocallisto/devops-upload-app:1.0.0
   ```

### Using Docker Compose

The project uses Docker Compose to run multiple services together. The services include:
- Upload service (port 8001)
- Stats service (port 8002)
- Nginx proxy (port 8000)

To run with Docker Compose:

1. Create a `.env` file with your API token:
   ```
   API_BEARER_TOKEN=your_secret_token
   ```

2. Build and start all services:
   ```bash
   docker compose build
   docker compose up -d
   ```

3. Access the services:
   - Main API Gateway: http://localhost:8000
   - Upload Service: http://localhost:8001
   - Stats Service: http://localhost:8002

4. To stop the services:
   ```bash
   docker compose down
   ```

The services share a common volume `my-uploads` for file storage and are connected through the `app-net` network.