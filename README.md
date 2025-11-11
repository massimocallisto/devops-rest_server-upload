# Upload API Service

## Description

A secure FastAPI-based service that allows authenticated users to upload and manage ZIP files. The service provides
endpoints for file upload and listing uploaded files, protected by bearer token authentication.

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
   docker run -p 8000:8000 -e API_TOKEN=your_secret_token massimocallisto/devops-upload-app:1.0.0
   ```

### Using Docker Compose

1. Create a `.env` file with your API token:
   ```
   API_TOKEN=your_secret_token
   ```
2. Start the service:
   ```bash
   docker-compose up
   ```

The service will be available at http://localhost:8000
