# Step-by-Step: Da Docker Compose a Kubernetes (DigitalOcean)

Nota che il file kubeconfig lo possiamo posizionare nella cartella dell'utente 
in `.kube/config` e salvarlo con il nome `default`.
In questo modo non dobbiamo ogni volta passare il kubeconfig manualmente.

## Step 1 – Secret e PVC
File: `00-secret-pvc.yaml`
Crea il namespace, un Secret per il token e un volume persistente (PVC).

```bash
kubectl apply -f 00-secret-pvc.yaml
```

## Step 2 – Deployment
File: `01-deployment.yaml`
Crea il Deployment per il container, monta il volume e usa il Secret per la variabile d'ambiente.

```bash
kubectl apply -f 01-deployment.yaml
kubectl get pods -n gestionale
```

## Step 3 – Service
File: `02-service.yaml`
Espone il Deployment con un Service di tipo LoadBalancer (DigitalOcean assegnerà un IP pubblico).

```bash
kubectl apply -f 02-service.yaml
kubectl get svc -n gestionale
```

Quando l'EXTERNAL-IP è pronto:
```bash
http://<EXTERNAL-IP>:8000/docs
```

Oppure
```bash
curl http://<EXTERNAL-IP>:8000/uploads -H "Authorization: Bearer YOUR_TOKEN"
```

## Prometheus e Grafana
Reference: https://www.digitalocean.com/community/developer-center/how-to-install-prometheus-monitoring-stack-for-doks-cluster

```
HELM_CHART_VERSION="79.6.1"

helm install kube-prom-stack prometheus-community/kube-prometheus-stack --version "${HELM_CHART_VERSION}" \
  --namespace monitoring \
  --create-namespace
```
Credenziali Grafana

```
Get Grafana 'admin' user password by running:
  kubectl --namespace monitoring get secrets kube-prom-stack-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo
```

### Fix problemi ServiceMonitoring custom app
Riferimento: https://github.com/prometheus-operator/kube-prometheus/issues/1392

```
helm upgrade kube-prom-stack prometheus-community/kube-prometheus-stack \
--namespace monitoring --values values.yml
```


