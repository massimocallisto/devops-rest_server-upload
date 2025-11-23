# Step-by-Step: Da Docker Compose a Kubernetes (DigitalOcean)

## Step 1 – Docker Compose
File: `step1-compose/docker-compose.yml`
Definisce un container singolo con volume e variabile d'ambiente.

## Step 2 – Secret e PVC
File: `step2-secret-pvc/secret-pvc.yaml`
Crea il namespace, un Secret per il token e un volume persistente (PVC).

```bash
kubectl apply -f step2-secret-pvc/secret-pvc.yaml
```

## Step 3 – Deployment
File: `step3-deployment/deployment.yaml`
Crea il Deployment per il container, monta il volume e usa il Secret per la variabile d'ambiente.

```bash
kubectl apply -f step3-deployment/deployment.yaml
kubectl get pods -n servizi
```

## Step 4 – Service
File: `step4-service/service.yaml`
Espone il Deployment con un Service di tipo LoadBalancer (DigitalOcean assegnerà un IP pubblico).

```bash
kubectl apply -f step4-service/service.yaml
kubectl get svc -n servizi
```

Quando l'EXTERNAL-IP è pronto:
```bash
curl http://<EXTERNAL-IP>:8000/status -H "Authorization: Bearer YOUR_TOKEN"
```
