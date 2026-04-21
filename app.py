"""
API Flask pour Détection d'Intrusions Réseau
Backend pour le Dashboard Network IDS
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import json
import os
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration CORS pour permettre les requêtes depuis le frontend
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # En production, restreindre aux domaines autorisés
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Classe pour gérer le modèle
class NetworkIDSModel:
    def __init__(self, model_dir='models'):
        """Initialisation du modèle"""
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.metadata = {}
        self.load_model()
    
    def load_model(self):
        """Charge le modèle et les preprocesseurs"""
        try:
            # Vérifier si les fichiers existent
            model_path = os.path.join(self.model_dir, 'best_model.pkl')
            scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
            encoder_path = os.path.join(self.model_dir, 'label_encoder.pkl')
            metadata_path = os.path.join(self.model_dir, 'metadata.json')
            
            if not all(os.path.exists(p) for p in [model_path, scaler_path, encoder_path]):
                logger.warning("⚠️ Modèles non trouvés - Mode simulation activé")
                self.simulation_mode = True
                self._init_simulation_mode()
                return
            
            # Charger les modèles
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.label_encoder = joblib.load(encoder_path)
            
            # Charger les métadonnées
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            
            self.simulation_mode = False
            logger.info(f"✅ Modèle chargé: {self.metadata.get('best_model', 'Unknown')}")
            logger.info(f"✅ Précision: {self.metadata.get('best_accuracy', 0)*100:.2f}%")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle: {str(e)}")
            logger.warning("⚠️ Basculement en mode simulation")
            self.simulation_mode = True
            self._init_simulation_mode()
    
    def _init_simulation_mode(self):
        """Initialise le mode simulation"""
        self.metadata = {
            'best_model': 'Simulation',
            'best_accuracy': 0.995,
            'num_features': 41,
            'num_classes': 5,
            'classes': ['DoS', 'Normal', 'Probe', 'R2L', 'U2R']
        }
        logger.info("🎮 Mode simulation initialisé")
    
    def predict(self, features):
        """Prédiction sur un échantillon"""
        try:
            if self.simulation_mode:
                return self._simulate_prediction(features)
            
            # Normalisation des features
            features_scaled = self.scaler.transform([features])
            
            # Prédiction
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0]
            
            # Conversion du label
            attack_type = self.label_encoder.inverse_transform([prediction])[0]
            confidence = float(np.max(probability))
            
            # Construction du résultat
            result = {
                'attack_type': attack_type,
                'is_attack': attack_type != 'Normal',
                'confidence': confidence,
                'severity': self._get_severity(attack_type, confidence),
                'probabilities': {
                    self.label_encoder.classes_[i]: float(prob) 
                    for i, prob in enumerate(probability)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur de prédiction: {str(e)}")
            return self._simulate_prediction(features)
    
    def _simulate_prediction(self, features):
        """Génère une prédiction simulée"""
        attack_types = ['Normal', 'DoS', 'Probe', 'R2L', 'U2R']
        
        # 70% de trafic normal, 30% d'attaques
        is_attack = np.random.random() > 0.7
        attack_type = np.random.choice(attack_types[1:]) if is_attack else 'Normal'
        confidence = 0.7 + np.random.random() * 0.3
        
        result = {
            'attack_type': attack_type,
            'is_attack': is_attack,
            'confidence': float(confidence),
            'severity': self._get_severity(attack_type, confidence),
            'probabilities': {
                at: float(np.random.random()) for at in attack_types
            },
            'simulation': True
        }
        
        # Normaliser les probabilités
        total = sum(result['probabilities'].values())
        result['probabilities'] = {
            k: v/total for k, v in result['probabilities'].items()
        }
        
        return result
    
    def _get_severity(self, attack_type, confidence):
        """Calcule la sévérité de l'attaque"""
        if attack_type == 'Normal':
            return 'info'
        
        severity_map = {
            'DoS': 'critical',
            'U2R': 'critical',
            'R2L': 'high',
            'Probe': 'medium'
        }
        
        base_severity = severity_map.get(attack_type, 'medium')
        
        # Réduire la sévérité si faible confiance
        if confidence < 0.7:
            severity_levels = {
                'critical': 'high',
                'high': 'medium',
                'medium': 'low'
            }
            return severity_levels.get(base_severity, 'low')
        
        return base_severity

# Initialisation du modèle
ids_model = NetworkIDSModel()

# Routes de l'API

@app.route('/')
def index():
    """Page d'accueil de l'API"""
    return jsonify({
        'name': 'Network IDS API',
        'version': '1.0',
        'status': 'online',
        'endpoints': [
            '/health',
            '/predict',
            '/batch_predict'
        ],
        'documentation': 'https://github.com/votre-username/network-ids'
    })

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé de l'API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model': ids_model.metadata.get('best_model', 'Unknown'),
        'version': '1.0',
        'mode': 'simulation' if ids_model.simulation_mode else 'production',
        'accuracy': ids_model.metadata.get('best_accuracy', 0)
    })

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    """
    Endpoint de prédiction
    
    Body (JSON):
    {
        "features": [41 valeurs],
        "timestamp": "ISO timestamp",
        "source_ip": "192.168.1.100",
        "dest_ip": "10.0.0.50"
    }
    """
    # Gérer les requêtes OPTIONS pour CORS
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        features = data.get('features')
        
        if not features:
            return jsonify({'error': 'Missing features field'}), 400
        
        if len(features) != ids_model.metadata.get('num_features', 41):
            return jsonify({
                'error': f'Invalid number of features. Expected {ids_model.metadata.get("num_features", 41)}, got {len(features)}'
            }), 400
        
        # Prédiction
        result = ids_model.predict(features)
        
        # Enrichissement avec métadonnées
        result['timestamp'] = data.get('timestamp', datetime.now().isoformat())
        result['source_ip'] = data.get('source_ip', 'Unknown')
        result['dest_ip'] = data.get('dest_ip', 'Unknown')
        
        # Génération d'alerte si attaque détectée
        if result['is_attack']:
            result['alert'] = generate_alert(result)
            result['recommendation'] = get_recommendation(result['attack_type'])
            
            # Log de l'alerte
            logger.warning(
                f"ATTACK DETECTED: {result['attack_type']} "
                f"from {result['source_ip']} "
                f"(confidence: {result['confidence']*100:.1f}%)"
            )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/batch_predict', methods=['POST', 'OPTIONS'])
def batch_predict():
    """
    Prédiction par batch
    
    Body (JSON):
    {
        "samples": [
            {"id": "1", "features": [...]},
            {"id": "2", "features": [...]}
        ]
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        samples = data.get('samples', [])
        
        if not samples:
            return jsonify({'error': 'No samples provided'}), 400
        
        results = []
        for sample in samples:
            features = sample.get('features')
            if features and len(features) == ids_model.metadata.get('num_features', 41):
                prediction = ids_model.predict(features)
                prediction['sample_id'] = sample.get('id')
                results.append(prediction)
        
        # Statistiques du batch
        stats = {
            'total_samples': len(results),
            'attacks_detected': sum(1 for r in results if r['is_attack']),
            'normal_traffic': sum(1 for r in results if not r['is_attack']),
            'attack_types': {}
        }
        
        for result in results:
            if result['is_attack']:
                attack_type = result['attack_type']
                stats['attack_types'][attack_type] = stats['attack_types'].get(attack_type, 0) + 1
        
        return jsonify({
            'predictions': results,
            'statistics': stats
        })
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_alert(result):
    """Génère une alerte structurée"""
    severity_icons = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢',
        'info': 'ℹ️'
    }
    
    return {
        'id': f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'title': f"{severity_icons[result['severity']]} {result['attack_type']} Attack Detected",
        'severity': result['severity'],
        'confidence': result['confidence'],
        'timestamp': result.get('timestamp', datetime.now().isoformat()),
        'source': result.get('source_ip', 'Unknown'),
        'destination': result.get('dest_ip', 'Unknown'),
        'requires_action': result['severity'] in ['critical', 'high']
    }

def get_recommendation(attack_type):
    """Recommandations de mitigation par type d'attaque"""
    recommendations = {
        'DoS': [
            "Bloquer l'adresse IP source",
            "Activer la limitation de débit (rate limiting)",
            "Vérifier la capacité réseau et serveur",
            "Contacter le FAI si l'attaque persiste"
        ],
        'Probe': [
            "Surveiller l'activité de reconnaissance",
            "Renforcer les règles de pare-feu",
            "Désactiver les services non essentiels",
            "Activer la détection de scan de ports"
        ],
        'R2L': [
            "Vérifier les journaux d'authentification",
            "Forcer la réinitialisation des mots de passe",
            "Activer l'authentification multi-facteurs",
            "Isoler les comptes compromis"
        ],
        'U2R': [
            "URGENCE: Escalade de privilèges détectée",
            "Isoler immédiatement le système affecté",
            "Lancer une analyse forensique complète",
            "Vérifier l'intégrité du système",
            "Appliquer les correctifs de sécurité"
        ]
    }
    
    return recommendations.get(attack_type, ["Surveiller l'activité réseau"])

# Gestion des erreurs
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Démarrage de l'API sur le port {port}")
    logger.info(f"🔧 Mode: {'Debug' if debug else 'Production'}")
    logger.info(f"🎮 Simulation: {'Activé' if ids_model.simulation_mode else 'Désactivé'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
