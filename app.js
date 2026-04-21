// Configuration de l'API
const API_CONFIG = {
    baseURL: localStorage.getItem('apiUrl') || 'https://your-backend-url.onrender.com',
    endpoints: {
        health: '/health',
        predict: '/predict',
        batchPredict: '/batch_predict'
    }
};

// État global de l'application
const appState = {
    monitoring: false,
    alerts: [],
    trafficCount: 0,
    attackCount: 0,
    attackTypes: {
        'Normal': 0,
        'DoS': 0,
        'Probe': 0,
        'R2L': 0,
        'U2R': 0
    }
};

// Charts
let trafficChart = null;
let attackTypesChart = null;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

// Initialisation de l'application
function initializeApp() {
    console.log('🚀 Initialisation du Network IDS Dashboard...');
    
    // Charger l'URL de l'API depuis le localStorage
    const apiUrlInput = document.getElementById('apiUrl');
    if (apiUrlInput) {
        apiUrlInput.value = API_CONFIG.baseURL;
        apiUrlInput.addEventListener('change', (e) => {
            API_CONFIG.baseURL = e.target.value;
            localStorage.setItem('apiUrl', e.target.value);
            showNotification('URL API mise à jour', 'success');
        });
    }
    
    // Initialiser les graphiques
    initializeCharts();
    
    // Vérifier la santé de l'API au démarrage
    checkAPIHealth();
    
    // Configurer le bouton de monitoring
    const monitorBtn = document.getElementById('startMonitoring');
    if (monitorBtn) {
        monitorBtn.addEventListener('click', toggleMonitoring);
    }
    
    // Mettre à jour l'heure
    updateLastCheck();
    setInterval(updateLastCheck, 1000);
    
    // Générer des données de démonstration
    simulateDemoData();
    
    console.log('✅ Application initialisée avec succès!');
}

// Tester l'API
async function testAPI() {
    const resultBox = document.getElementById('apiTestResult');
    const responseBox = document.getElementById('apiResponse');
    
    // Afficher le spinner
    responseBox.innerHTML = '<div class="spinner"></div>';
    resultBox.style.display = 'block';
    
    try {
        // Test de l'endpoint health
        const healthResponse = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.health}`);
        
        if (!healthResponse.ok) {
            throw new Error(`Erreur HTTP: ${healthResponse.status}`);
        }
        
        const healthData = await healthResponse.json();
        
        // Test de prédiction avec des données aléatoires
        const testFeatures = Array.from({length: 41}, () => Math.random());
        
        const predictResponse = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.predict}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                features: testFeatures,
                source_ip: '192.168.1.100',
                dest_ip: '10.0.0.50'
            })
        });
        
        if (!predictResponse.ok) {
            throw new Error(`Erreur de prédiction: ${predictResponse.status}`);
        }
        
        const predictData = await predictResponse.json();
        
        // Afficher les résultats
        const result = {
            health: healthData,
            prediction: predictData,
            status: 'SUCCESS ✅'
        };
        
        responseBox.innerHTML = JSON.stringify(result, null, 2);
        
        // Afficher une notification
        showNotification('Test API réussi!', 'success');
        
        // Mettre à jour le statut système
        document.getElementById('systemStatus').textContent = 'En ligne';
        document.getElementById('systemStatus').parentElement.parentElement.className = 
            'status-card status-card-green';
        
    } catch (error) {
        console.error('Erreur lors du test API:', error);
        
        responseBox.innerHTML = JSON.stringify({
            status: 'ERROR ❌',
            error: error.message,
            solution: 'Vérifiez que:\n1. L\'API backend est déployée\n2. L\'URL est correcte\n3. CORS est configuré'
        }, null, 2);
        
        showNotification('Erreur de connexion à l\'API', 'error');
        
        // Mettre à jour le statut système
        document.getElementById('systemStatus').textContent = 'Hors ligne';
        document.getElementById('systemStatus').parentElement.parentElement.className = 
            'status-card status-card-orange';
    }
}

// Vérifier la santé de l'API
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.health}`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            document.getElementById('systemStatus').textContent = 'En ligne';
            console.log('✅ API en ligne');
        }
    } catch (error) {
        document.getElementById('systemStatus').textContent = 'Vérification...';
        console.log('⚠️ API non accessible (normal si pas encore déployée)');
    }
}

// Basculer le monitoring
function toggleMonitoring() {
    appState.monitoring = !appState.monitoring;
    const btn = document.getElementById('startMonitoring');
    
    if (appState.monitoring) {
        btn.innerHTML = '<i class="fas fa-stop"></i> Arrêter';
        btn.className = 'btn btn-danger';
        startMonitoring();
        showNotification('Monitoring démarré', 'success');
    } else {
        btn.innerHTML = '<i class="fas fa-play"></i> Démarrer';
        btn.className = 'btn btn-success';
        showNotification('Monitoring arrêté', 'info');
    }
}

// Démarrer le monitoring
function startMonitoring() {
    if (!appState.monitoring) return;
    
    // Simuler l'analyse de trafic
    setTimeout(() => {
        analyzeRandomTraffic();
        startMonitoring();
    }, 2000);
}

// Analyser du trafic aléatoire (simulation)
async function analyzeRandomTraffic() {
    try {
        const features = Array.from({length: 41}, () => Math.random());
        
        const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.predict}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                features: features,
                source_ip: generateRandomIP(),
                dest_ip: generateRandomIP()
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            processAnalysisResult(result);
        }
    } catch (error) {
        console.log('Mode simulation - API non accessible');
        // Continuer en mode simulation
        processAnalysisResult(generateSimulatedResult());
    }
}

// Traiter le résultat d'analyse
function processAnalysisResult(result) {
    // Incrémenter le compteur de trafic
    appState.trafficCount++;
    document.getElementById('trafficCount').textContent = appState.trafficCount.toLocaleString();
    
    // Si c'est une attaque
    if (result.is_attack) {
        appState.attackCount++;
        document.getElementById('attackCount').textContent = appState.attackCount;
        
        // Mettre à jour la distribution des types d'attaques
        const attackType = result.attack_type;
        if (appState.attackTypes[attackType] !== undefined) {
            appState.attackTypes[attackType]++;
        }
        
        // Ajouter une alerte
        addAlert(result);
    } else {
        appState.attackTypes['Normal']++;
    }
    
    // Mettre à jour les graphiques
    updateCharts();
}

// Ajouter une alerte
function addAlert(result) {
    const alert = {
        id: Date.now(),
        title: result.alert ? result.alert.title : `${result.attack_type} détecté`,
        severity: result.severity || 'medium',
        timestamp: new Date().toLocaleString('fr-FR'),
        source: result.source_ip || 'Unknown',
        destination: result.dest_ip || 'Unknown',
        confidence: result.confidence || 0,
        recommendations: result.recommendation || []
    };
    
    appState.alerts.unshift(alert);
    
    // Limiter à 50 alertes
    if (appState.alerts.length > 50) {
        appState.alerts.pop();
    }
    
    // Mettre à jour l'affichage
    updateAlertsDisplay();
    updateAlertBadge();
}

// Mettre à jour l'affichage des alertes
function updateAlertsDisplay() {
    const container = document.getElementById('alertsContainer');
    
    if (appState.alerts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>Aucune alerte pour le moment</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = appState.alerts.map(alert => `
        <div class="alert-item ${alert.severity}">
            <div class="alert-header">
                <div class="alert-title">${alert.title}</div>
                <div class="alert-time">${alert.timestamp}</div>
            </div>
            <div class="alert-body">
                Attaque détectée avec une confiance de ${(alert.confidence * 100).toFixed(1)}%
            </div>
            <div class="alert-details">
                <div class="alert-detail">
                    <strong>Source:</strong> ${alert.source}
                </div>
                <div class="alert-detail">
                    <strong>Destination:</strong> ${alert.destination}
                </div>
                <div class="alert-detail">
                    <strong>Sévérité:</strong> ${alert.severity.toUpperCase()}
                </div>
            </div>
        </div>
    `).join('');
}

// Mettre à jour le badge d'alertes
function updateAlertBadge() {
    const badge = document.getElementById('alertCount');
    badge.textContent = appState.alerts.length;
}

// Effacer les alertes
function clearAlerts() {
    if (confirm('Voulez-vous effacer toutes les alertes?')) {
        appState.alerts = [];
        updateAlertsDisplay();
        updateAlertBadge();
        showNotification('Alertes effacées', 'info');
    }
}

// Initialiser les graphiques
function initializeCharts() {
    // Graphique de trafic
    const trafficCtx = document.getElementById('trafficChart');
    if (trafficCtx) {
        trafficChart = new Chart(trafficCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Trafic Normal',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Attaques',
                    data: [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Graphique de distribution des attaques
    const attackTypesCtx = document.getElementById('attackTypesChart');
    if (attackTypesCtx) {
        attackTypesChart = new Chart(attackTypesCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(appState.attackTypes),
                datasets: [{
                    data: Object.values(appState.attackTypes),
                    backgroundColor: [
                        '#10b981',
                        '#ef4444',
                        '#f59e0b',
                        '#8b5cf6',
                        '#06b6d4'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right'
                    }
                }
            }
        });
    }
}

// Mettre à jour les graphiques
function updateCharts() {
    // Mettre à jour le graphique de distribution
    if (attackTypesChart) {
        attackTypesChart.data.datasets[0].data = Object.values(appState.attackTypes);
        attackTypesChart.update();
    }
    
    // Mettre à jour le graphique de trafic (garder les 20 derniers points)
    if (trafficChart) {
        const time = new Date().toLocaleTimeString('fr-FR');
        
        trafficChart.data.labels.push(time);
        trafficChart.data.datasets[0].data.push(appState.attackTypes['Normal']);
        trafficChart.data.datasets[1].data.push(appState.attackCount);
        
        if (trafficChart.data.labels.length > 20) {
            trafficChart.data.labels.shift();
            trafficChart.data.datasets[0].data.shift();
            trafficChart.data.datasets[1].data.shift();
        }
        
        trafficChart.update();
    }
}

// Générer une IP aléatoire
function generateRandomIP() {
    return `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
}

// Générer un résultat simulé
function generateSimulatedResult() {
    const attackTypes = ['Normal', 'DoS', 'Probe', 'R2L', 'U2R'];
    const severities = ['info', 'low', 'medium', 'high', 'critical'];
    
    const isAttack = Math.random() > 0.7;
    const attackType = isAttack ? attackTypes[Math.floor(Math.random() * (attackTypes.length - 1)) + 1] : 'Normal';
    
    return {
        attack_type: attackType,
        is_attack: isAttack,
        confidence: 0.7 + Math.random() * 0.3,
        severity: isAttack ? severities[Math.floor(Math.random() * severities.length)] : 'info',
        source_ip: generateRandomIP(),
        dest_ip: generateRandomIP(),
        alert: isAttack ? {
            title: `${attackType} Attack Detected`
        } : null,
        recommendation: isAttack ? ['Monitor network activity', 'Check firewall rules'] : []
    };
}

// Simuler des données de démonstration
function simulateDemoData() {
    // Générer quelques alertes de démo
    for (let i = 0; i < 3; i++) {
        setTimeout(() => {
            const result = generateSimulatedResult();
            if (result.is_attack) {
                processAnalysisResult(result);
            }
        }, i * 1000);
    }
}

// Mettre à jour l'heure de la dernière vérification
function updateLastCheck() {
    const now = new Date();
    document.getElementById('lastCheck').textContent = now.toLocaleTimeString('fr-FR');
}

// Afficher une notification
function showNotification(message, type = 'info') {
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Ajouter au DOM
    document.body.appendChild(notification);
    
    // Animer l'entrée
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Retirer après 3 secondes
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Style CSS pour les notifications (à ajouter au CSS)
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        background: white;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        z-index: 9999;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        border-left: 4px solid #10b981;
        color: #10b981;
    }
    
    .notification-error {
        border-left: 4px solid #ef4444;
        color: #ef4444;
    }
    
    .notification-info {
        border-left: 4px solid #4f46e5;
        color: #4f46e5;
    }
`;
document.head.appendChild(notificationStyles);

console.log('📱 Network IDS Dashboard chargé');
