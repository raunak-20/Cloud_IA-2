# Flask Application Deployment on AWS EC2 with Docker & Kubernetes

A clean, production-ready Flask application containerized with **Docker** and orchestrated using **Kubernetes** (`minikube`), featuring an interactive dashboard for monitoring pod routing, live health checks, and load balancing.

---

## 📁 Project Structure

```text
.
├── app.py              # Flask application with interactive dashboard & REST endpoints
├── requirements.txt    # Python dependencies (Flask, Gunicorn)
├── Dockerfile          # Multi-stage optimized Dockerfile running non-root user
├── .dockerignore       # Build context exclusion rules
├── deployment.yaml     # Kubernetes Deployment (3 replicas, probes, resource limits)
├── service.yaml        # Kubernetes NodePort Service (Port 80 -> 5000, NodePort 30007)
└── README.md           # Step-by-step deployment and verification guide
```

---

## 🚀 Application Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | **Browser:** Interactive Dark-themed Dashboard<br>**curl / JSON:** Returns `{"message": "...", "pod_hostname": "...", "version": "1.0"}` |
| `/api/info` | `GET` | Returns pod metadata, uptime, and request counters in JSON format |
| `/health` | `GET` | Readiness & Liveness probe endpoint returning HTTP 200 `{"status": "healthy"}` |

---

## 🛠️ Prerequisites (AWS EC2 Setup)

1. **EC2 Instance:** Ubuntu 22.04 / 24.04 LTS (Recommended: `t2.medium` or `t3.medium` with at least 2 vCPUs and 4 GB RAM for Minikube).
2. **Security Group Inbound Rules:**
   - `SSH` (Port `22`) - Your IP
   - `Custom TCP` (Port `5000`) - Container direct testing
   - `Custom TCP` (Port `8080`) - Port-forwarding access
   - `Custom TCP` (Port `30007`) - Kubernetes NodePort access
   - `HTTP` (Port `80`) - General web access

---

## 📋 Step-by-Step Deployment Guide

### Step 1: System Package Update

SSH into your EC2 instance and update package repositories:

```bash
sudo -i
sudo apt update -y
```

---

### Step 2: Install Docker

Install Docker Engine:

```bash
sudo apt install docker.io -y
systemctl enable --now docker
```

*(Optional: Add your user to the docker group if not running as root)*:
```bash
sudo usermod -aG docker $USER
```

---

### Step 3: Clone or Transfer the Project

Clone your repository into the workspace:

```bash
git clone https://github.com/Pranaykarmankar/IA2.git
cd IA2
```

---

### Step 4: Review the Dockerfile

The `Dockerfile` builds a lightweight image using `python:3.12-slim`, installs requirements, creates a non-root `appuser`, and runs with `gunicorn` on port 5000:

```dockerfile
# Base image: small official Python image
FROM python:3.12-slim

# Avoid .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Working directory inside the container
WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

# Document the port the app listens on
EXPOSE 5000

# Start the app with gunicorn (production-grade server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

---

### Step 5: Build the Docker Image

Build and tag the container image:

```bash
docker build -t flask-k8s-demo:1.0 .
```

---

### Step 6: Verify the Image

Verify that `flask-k8s-demo:1.0` appears in the local Docker image list:

```bash
docker images
```

---

### Step 7: Test the Container Locally

Run a test container and verify via `curl`:

```bash
docker run -d --name flask-container -p 5000:5000 flask-k8s-demo:1.0
docker ps
curl http://localhost:5000/
```

**Expected output:**
```json
{"message":"Hello from a containerized Flask app!","pod_hostname":"e9965315e088","version":"1.0"}
```

Clean up the test container:
```bash
docker stop flask-container && docker rm flask-container
```

---

### Step 8: Install kubectl and Minikube

Download and install the Kubernetes CLI (`kubectl`) and `minikube`:

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl

# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

---

### Step 9: Start the Kubernetes Cluster

Launch Minikube with the Docker driver (using `--force` when running as root):

```bash
minikube start --driver=docker --force
```

Load your locally built image into the Minikube cluster:
```bash
minikube image load flask-k8s-demo:1.0
```

---

### Step 10 & 11: Review Kubernetes Manifests

#### `deployment.yaml`
Configures a 3-replica deployment with health probes and resource limits:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-app
  labels:
    app: flask-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flask-app
  template:
    metadata:
      labels:
        app: flask-app
    spec:
      containers:
        - name: flask-app
          image: flask-k8s-demo:1.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
          env:
            - name: APP_VERSION
              value: "1.0"
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 3
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 10
            periodSeconds: 10
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 128Mi
```

#### `service.yaml`
Exposes the pods as a NodePort Service:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: flask-service
spec:
  type: NodePort
  selector:
    app: flask-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
      nodePort: 30007
```

---

### Step 12: Deploy the Application

Apply the manifests and verify pod readiness:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check pods status (all 3 should reach 'Running' status)
kubectl get pods -o wide

# Check service status
kubectl get svc
```

Forward port 80 to 8080 on all network interfaces:
```bash
kubectl port-forward --address 0.0.0.0 service/flask-service 8080:80
```

---

### Step 13: Access the Application in Your Browser

Open your browser and navigate to:
```text
http://<YOUR_EC2_PUBLIC_IP>:8080
```

The interactive dashboard allows you to:
- **Served by pod:** Displays the active pod hostname, uptime, and request count.
- **Health Check (/health):** Verifies the liveness/readiness probe.
- **Load Balancing:** Sends 30 concurrent requests to observe traffic distribution across the 3 pods.
- **Live Monitor:** Polls the cluster every second. Try opening another terminal and running:
  ```bash
  kubectl delete pod <pod-name>
  ```
  Watch Kubernetes automatically terminate the pod and create a replacement pod without any downtime!

