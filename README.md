# 📦 Modèles IA pour Network IDS

## 📋 Description

Ce dossier contient les modèles d'Intelligence Artificielle entraînés pour la détection d'intrusions réseau.

## 🎮 Mode Actuel: SIMULATION

L'application fonctionne actuellement en **mode simulation**.
Elle génère des prédictions aléatoires pour la démonstration.

## 🚀 Comment Ajouter les Modèles Réels?

### Étape 1: Entraîner les Modèles sur Google Colab

1. Ouvrir `NetworkSecurityAI_Bootcamp.ipynb` dans Google Colab
2. Exécuter toutes les cellules
3. Télécharger l'archive `network_ids_models_XXXXXXXX.zip`

### Étape 2: Extraire les Fichiers

```bash
# Extraire l'archive
unzip network_ids_models_XXXXXXXX.zip

# Les fichiers suivants doivent être présents:
# - best_model.pkl         (Modèle principal)
# - scaler.pkl             (Normalisateur)
# - label_encoder.pkl      (Encodeur de labels)
# - metadata.json          (Métadonnées)
```

### Étape 3: Placer les Fichiers Ici

```
backend/
├── models/                    ← Vous êtes ici
│   ├── best_model.pkl         ← Copier ici
│   ├── scaler.pkl             ← Copier ici
│   ├── label_encoder.pkl      ← Copier ici
│   └── metadata.json          ← Copier ici
└── app.py
```

### Étape 4: Redéployer sur Render

```bash
# Depuis la racine du projet
git add backend/models/
git commit -m "Add trained ML models"
git push

# Render redéploiera automatiquement
# L'API basculera du mode simulation au mode production
```

## 📊 Fichiers Attendus

| Fichier | Taille (approx) | Description |
|---------|-----------------|-------------|
| `best_model.pkl` | 5-50 MB | Modèle principal (XGBoost/Random Forest) |
| `scaler.pkl` | < 1 KB | StandardScaler pour normalisation |
| `label_encoder.pkl` | < 1 KB | LabelEncoder pour les classes |
| `metadata.json` | < 1 KB | Métadonnées (précision, classes, etc.) |

## ⚙️ Configuration Automatique

Le fichier `app.py` détecte automatiquement la présence des modèles:

```python
# Mode Production (modèles présents)
✅ Modèle chargé: XGBoost
✅ Précision: 99.50%
🎯 Mode: production

# Mode Simulation (modèles absents)
⚠️ Modèles non trouvés - Mode simulation activé
🎮 Mode simulation initialisé
```

## 🔍 Vérification

Pour vérifier que les modèles sont chargés:

```bash
# Tester l'API
curl https://your-backend-url.onrender.com/health

# Résultat avec modèles:
{
  "status": "healthy",
  "model": "XGBoost",
  "mode": "production",
  "accuracy": 0.995
}

# Résultat en simulation:
{
  "status": "healthy",
  "model": "Simulation",
  "mode": "simulation"
}
```

## 🎯 Recommandations

### Pour le Développement
- Garder le mode simulation
- Plus rapide à déployer
- Aucune dépendance lourde

### Pour la Production
- Ajouter les modèles réels
- Meilleure précision (99.5%)
- Détection basée sur données réelles

## 📝 Notes Importantes

⚠️ **Taille des Modèles**
- Les modèles peuvent être volumineux (5-50 MB)
- Augmente le temps de déploiement
- Considérer l'utilisation de Git LFS pour les gros fichiers

⚠️ **Performance**
- Avec modèles: ~100ms par prédiction
- Sans modèles (simulation): ~10ms par prédiction

⚠️ **Mémoire**
- Render Free tier: 512 MB RAM
- Les modèles utilisent ~100-200 MB
- Vérifier que vous avez assez de RAM

## 🔗 Ressources

- [Guide d'entraînement Colab](../NetworkSecurityAI_Bootcamp.ipynb)
- [Documentation API](../README.md)
- [Git LFS Guide](https://git-lfs.github.com/)

---

**Mode actuel**: 🎮 Simulation

Pour passer en mode production, suivez les étapes ci-dessus.
