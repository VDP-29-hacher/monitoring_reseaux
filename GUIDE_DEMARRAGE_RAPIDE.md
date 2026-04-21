# 🚀 GUIDE DE DÉMARRAGE RAPIDE - IA Monitoring Réseau

## 📋 CHECKLIST AVANT DE COMMENCER

### ✅ Étape 1: Préparation de Google Colab
1. Ouvrir le fichier `NetworkSecurityAI_Bootcamp.ipynb` dans Google Colab
2. Activer le GPU: `Runtime` → `Change runtime type` → `Hardware accelerator: GPU`
3. Vérifier la connexion: cliquer sur le symbole ✓ en haut à droite

### ✅ Étape 2: Exécution du Notebook
Exécuter les cellules dans l'ordre:

1. **Partie 1-2**: Installation + Données (3-5 min)
2. **Partie 3-5**: Exploration + Preprocessing (2-3 min)
3. **Partie 6-7**: Entraînement des modèles (10-15 min)
   - Random Forest: ~45s
   - XGBoost: ~40s
   - LightGBM: ~30s
   - Neural Network: ~2-3 min
4. **Partie 8-9**: Évaluation + Sauvegarde (1-2 min)
5. **Partie 10-12**: API + Documentation (immédiat)

**Temps total estimé: 20-30 minutes**

---

## 📥 RÉCUPÉRATION DES MODÈLES

Après l'exécution complète:

```python
# Dans Colab, télécharger l'archive
from google.colab import files
files.download('network_ids_models_XXXXXXXX.zip')
```

Le fichier ZIP contient:
- ✅ Modèles ML (Random Forest, XGBoost, LightGBM)
- ✅ Réseau de neurones (Keras/TensorFlow)
- ✅ Preprocesseurs (Scaler, LabelEncoder)
- ✅ Métadonnées (précision, classes, etc.)

---

## 🖥️ INSTALLATION LOCALE

### Sur votre serveur Linux/Windows:

```bash
# 1. Extraire l'archive
unzip network_ids_models_XXXXXXXX.zip
cd network_ids_models_XXXXXXXX

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Tester l'API
python network_ids_api.py
```

Dans un autre terminal:
```bash
# Test de l'API
curl http://localhost:5000/health
```

**Résultat attendu:**
```json
{
    "status": "healthy",
    "timestamp": "2024-04-17T12:00:00",
    "model": "Network IDS",
    "version": "1.0"
}
```

---

## 🔧 CONFIGURATION POUR VOTRE RÉSEAU

### Étape 1: Identifier votre interface réseau

**Linux:**
```bash
ifconfig
# ou
ip addr show
```

**Windows:**
```powershell
ipconfig
```

Recherchez votre interface active (ex: `eth0`, `wlan0`, `en0`)

### Étape 2: Modifier `real_time_monitor.py`

```python
monitor = NetworkMonitor(
    api_url="http://localhost:5000",
    interface="eth0"  # ← REMPLACER par votre interface
)
```

### Étape 3: Lancer le monitoring

**Linux/Mac:**
```bash
sudo python real_time_monitor.py
```

**Windows (PowerShell Admin):**
```powershell
python real_time_monitor.py
```

---

## 🧪 TEST DE FONCTIONNEMENT

### Test 1: API de prédiction

Créer un fichier `test_api.py`:

```python
import requests
import numpy as np

# Features de test (41 valeurs)
test_features = np.random.rand(41).tolist()

response = requests.post('http://localhost:5000/predict', json={
    'features': test_features,
    'source_ip': '192.168.1.100',
    'dest_ip': '10.0.0.50'
})

result = response.json()
print(f"Type d'attaque: {result['attack_type']}")
print(f"Est une attaque: {result['is_attack']}")
print(f"Confiance: {result['confidence']*100:.1f}%")
```

Exécuter:
```bash
python test_api.py
```

### Test 2: Monitoring en mode simulation

Pour tester sans capture réelle, modifier `real_time_monitor.py`:

```python
# Ajouter cette fonction de test
def simulate_traffic():
    for i in range(10):
        features = np.random.rand(41).tolist()
        result = requests.post('http://localhost:5000/predict', json={
            'features': features,
            'source_ip': f'192.168.1.{100+i}',
            'dest_ip': '10.0.0.50'
        })
        print(f"[{i+1}/10] {result.json()['attack_type']}")
        time.sleep(0.5)

if __name__ == '__main__':
    simulate_traffic()
```

---

## 🔗 INTÉGRATION AVEC VOTRE APPLICATION

### Architecture Recommandée

```
┌─────────────────┐
│  Votre App      │
│  (Frontend)     │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  Flask API      │
│  (Port 5000)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  Modèle IA      │◄─────┤  Network     │
│  (Prédiction)   │      │  Monitor     │
└─────────────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│  Système        │
│  d'Alertes      │
└─────────────────┘
```

### Exemple d'intégration Frontend (JavaScript)

```javascript
// Dans votre application
async function analyzeNetworkTraffic(features) {
    try {
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                features: features,
                source_ip: sourceIP,
                dest_ip: destIP
            })
        });
        
        const result = await response.json();
        
        // Afficher l'alerte si attaque détectée
        if (result.is_attack) {
            showAlert({
                title: result.alert.title,
                severity: result.severity,
                recommendations: result.recommendation
            });
        }
        
        // Mettre à jour le dashboard
        updateDashboard(result);
        
        return result;
    } catch (error) {
        console.error('Erreur d\'analyse:', error);
    }
}
```

---

## 📊 FONCTIONNALITÉS DE VOTRE APP

### 1. Alertes & Triage
```python
# Intégration avec votre système d'alertes
def send_alert(alert):
    # Email
    send_email(
        to='admin@example.com',
        subject=alert['title'],
        body=f"Sévérité: {alert['severity']}\nSource: {alert['source']}"
    )
    
    # SMS (via Twilio)
    send_sms(
        to='+22670XXXXXX',
        message=f"⚠️ {alert['title']}"
    )
    
    # Webhook Discord/Slack
    send_webhook(
        url='https://hooks.slack.com/services/XXX',
        payload=alert
    )
```

### 2. Collecte des Logs
```python
import logging
import json

# Configuration du logger
logging.basicConfig(
    filename='network_ids.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_detection(result):
    logging.info(json.dumps({
        'attack_type': result['attack_type'],
        'confidence': result['confidence'],
        'source_ip': result['source_ip'],
        'dest_ip': result['dest_ip'],
        'timestamp': result['timestamp']
    }))
```

### 3. Threat Intelligence
```python
# Base de données d'IP malveillantes
BLACKLIST_IPS = set()

def check_ip_reputation(ip):
    # Vérifier dans la blacklist locale
    if ip in BLACKLIST_IPS:
        return 'malicious'
    
    # Vérifier avec des services externes
    # AbuseIPDB, VirusTotal, etc.
    response = requests.get(f'https://api.abuseipdb.com/api/v2/check?ipAddress={ip}')
    data = response.json()
    
    if data['data']['abuseConfidenceScore'] > 75:
        BLACKLIST_IPS.add(ip)
        return 'malicious'
    
    return 'clean'
```

### 4. Métriques Réseau
```python
from collections import defaultdict
import time

class NetworkMetrics:
    def __init__(self):
        self.connections = defaultdict(list)
    
    def record_connection(self, src_ip, dst_ip, bytes_transferred):
        timestamp = time.time()
        self.connections[f"{src_ip}:{dst_ip}"].append({
            'timestamp': timestamp,
            'bytes': bytes_transferred
        })
    
    def get_bandwidth(self, src_ip, dst_ip, window=60):
        """Bande passante sur les 60 dernières secondes"""
        key = f"{src_ip}:{dst_ip}"
        now = time.time()
        
        recent = [
            c['bytes'] for c in self.connections[key]
            if now - c['timestamp'] <= window
        ]
        
        return sum(recent) / window  # Bytes/sec
```

---

## 🚨 DÉPANNAGE RAPIDE

### Problème: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Problème: "Permission denied" (capture réseau)
```bash
sudo python real_time_monitor.py
# OU configurer les capabilities
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)
```

### Problème: "Model file not found"
Vérifier que le chemin est correct dans `network_ids_api.py`:
```python
ids_model = NetworkIDSModel('network_ids_models_20240417_120000')
#                            ↑ Remplacer par votre dossier
```

### Problème: API ne répond pas
```bash
# Vérifier que le port 5000 est libre
netstat -tulpn | grep 5000
# OU
lsof -i :5000

# Tuer le processus si nécessaire
kill -9 <PID>
```

---

## 📈 OPTIMISATIONS DE PRODUCTION

### 1. Performance
```python
# Utiliser Gunicorn pour production
pip install gunicorn

# Lancer avec plusieurs workers
gunicorn -w 4 -b 0.0.0.0:5000 network_ids_api:app
```

### 2. Mise en cache
```python
from functools import lru_cache
import redis

# Redis pour cache distribué
cache = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=1000)
def predict_cached(features_tuple):
    return ids_model.predict(list(features_tuple))
```

### 3. Load Balancing
```nginx
# Configuration Nginx
upstream api_backend {
    server localhost:5000;
    server localhost:5001;
    server localhost:5002;
}

server {
    listen 80;
    location /api/ {
        proxy_pass http://api_backend;
    }
}
```

---

## ✅ CHECKLIST DE MISE EN PRODUCTION

- [ ] Modèles entraînés et testés
- [ ] API Flask fonctionnelle
- [ ] Système d'alertes configuré
- [ ] Logs activés
- [ ] Monitoring CPU/RAM/Network
- [ ] Backup automatique des modèles
- [ ] Documentation à jour
- [ ] Tests de charge effectués
- [ ] Plan de reprise après incident
- [ ] Formation de l'équipe

---

## 📞 SUPPORT ET RESSOURCES

### Documentation
- README.md (complet)
- Code commenté dans le notebook
- API documentation (endpoints)

### Améliorations Futures
- [ ] Dashboard web temps réel
- [ ] Réentraînement automatique
- [ ] Détection de nouvelles attaques
- [ ] Intégration SIEM
- [ ] Analyse comportementale avancée
- [ ] Machine Learning explicable (XAI)

---

**Bon déploiement! 🚀**
