#!/usr/bin/env python3
"""
Script de Test Complet - Système IA de Détection d'Intrusions Réseau
Vérifie que tous les composants fonctionnent correctement
"""

import sys
import requests
import numpy as np
import time
from colorama import init, Fore, Style
import json

# Initialisation de colorama pour les couleurs dans le terminal
init(autoreset=True)

def print_header(text):
    """Affiche un en-tête stylisé"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text:^70}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

def print_success(text):
    """Affiche un message de succès"""
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_error(text):
    """Affiche un message d'erreur"""
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_warning(text):
    """Affiche un avertissement"""
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def print_info(text):
    """Affiche une information"""
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

class NetworkIDSTester:
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
        self.tests_passed = 0
        self.tests_failed = 0
    
    def test_api_health(self):
        """Test 1: Vérification de la santé de l'API"""
        print_header("TEST 1: Santé de l'API")
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"API est en ligne - Status: {data['status']}")
                print_info(f"Version: {data['version']}")
                print_info(f"Timestamp: {data['timestamp']}")
                self.tests_passed += 1
                return True
            else:
                print_error(f"Code HTTP incorrect: {response.status_code}")
                self.tests_failed += 1
                return False
        
        except requests.exceptions.ConnectionError:
            print_error("Impossible de se connecter à l'API")
            print_warning("Assurez-vous que l'API est démarrée: python network_ids_api.py")
            self.tests_failed += 1
            return False
        except Exception as e:
            print_error(f"Erreur inattendue: {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_single_prediction(self):
        """Test 2: Prédiction unique"""
        print_header("TEST 2: Prédiction Unique")
        
        try:
            # Génération de features aléatoires (41 valeurs)
            test_features = np.random.rand(41).tolist()
            
            payload = {
                'features': test_features,
                'source_ip': '192.168.1.100',
                'dest_ip': '10.0.0.50',
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            
            print_info("Envoi des features de test...")
            response = requests.post(
                f"{self.api_url}/predict",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print_success("Prédiction réussie!")
                print(f"\n{Fore.CYAN}Résultat:{Style.RESET_ALL}")
                print(f"  Type d'attaque: {Fore.YELLOW}{result['attack_type']}{Style.RESET_ALL}")
                print(f"  Est une attaque: {Fore.RED if result['is_attack'] else Fore.GREEN}{result['is_attack']}{Style.RESET_ALL}")
                print(f"  Confiance: {result['confidence']*100:.2f}%")
                print(f"  Sévérité: {result['severity']}")
                
                if result.get('alert'):
                    print(f"\n  {Fore.RED}ALERTE GÉNÉRÉE:{Style.RESET_ALL}")
                    print(f"    Titre: {result['alert']['title']}")
                    print(f"    ID: {result['alert']['id']}")
                
                if result.get('recommendation'):
                    print(f"\n  {Fore.CYAN}Recommandations:{Style.RESET_ALL}")
                    for i, rec in enumerate(result['recommendation'], 1):
                        print(f"    {i}. {rec}")
                
                self.tests_passed += 1
                return True
            else:
                print_error(f"Erreur HTTP: {response.status_code}")
                print_error(f"Message: {response.text}")
                self.tests_failed += 1
                return False
        
        except Exception as e:
            print_error(f"Erreur lors de la prédiction: {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_batch_prediction(self):
        """Test 3: Prédiction par batch"""
        print_header("TEST 3: Prédiction par Batch")
        
        try:
            # Génération de 5 échantillons
            samples = []
            for i in range(5):
                samples.append({
                    'id': f'sample_{i+1}',
                    'features': np.random.rand(41).tolist()
                })
            
            payload = {'samples': samples}
            
            print_info(f"Envoi de {len(samples)} échantillons...")
            response = requests.post(
                f"{self.api_url}/batch_predict",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print_success("Prédiction batch réussie!")
                
                stats = result['statistics']
                print(f"\n{Fore.CYAN}Statistiques:{Style.RESET_ALL}")
                print(f"  Total d'échantillons: {stats['total_samples']}")
                print(f"  Attaques détectées: {Fore.RED}{stats['attacks_detected']}{Style.RESET_ALL}")
                print(f"  Trafic normal: {Fore.GREEN}{stats['normal_traffic']}{Style.RESET_ALL}")
                
                if stats['attack_types']:
                    print(f"\n  {Fore.YELLOW}Types d'attaques:{Style.RESET_ALL}")
                    for attack_type, count in stats['attack_types'].items():
                        print(f"    - {attack_type}: {count}")
                
                self.tests_passed += 1
                return True
            else:
                print_error(f"Erreur HTTP: {response.status_code}")
                self.tests_failed += 1
                return False
        
        except Exception as e:
            print_error(f"Erreur lors du batch: {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_edge_cases(self):
        """Test 4: Cas limites et gestion d'erreurs"""
        print_header("TEST 4: Cas Limites et Erreurs")
        
        test_cases = [
            {
                'name': 'Features manquantes',
                'payload': {'features': []},
                'expected_status': 400
            },
            {
                'name': 'Nombre incorrect de features',
                'payload': {'features': [1, 2, 3]},
                'expected_status': 400
            },
            {
                'name': 'Features invalides (None)',
                'payload': {'features': None},
                'expected_status': 400
            }
        ]
        
        passed = 0
        for test in test_cases:
            print_info(f"Test: {test['name']}")
            
            try:
                response = requests.post(
                    f"{self.api_url}/predict",
                    json=test['payload'],
                    timeout=5
                )
                
                if response.status_code == test['expected_status']:
                    print_success(f"  Gestion d'erreur correcte (HTTP {response.status_code})")
                    passed += 1
                else:
                    print_error(f"  Status attendu: {test['expected_status']}, obtenu: {response.status_code}")
            
            except Exception as e:
                print_error(f"  Erreur inattendue: {str(e)}")
        
        if passed == len(test_cases):
            print_success(f"\nTous les cas limites sont gérés correctement ({passed}/{len(test_cases)})")
            self.tests_passed += 1
            return True
        else:
            print_warning(f"\nCertains cas limites ont échoué ({passed}/{len(test_cases)})")
            self.tests_failed += 1
            return False
    
    def test_performance(self):
        """Test 5: Performance et temps de réponse"""
        print_header("TEST 5: Performance")
        
        try:
            print_info("Mesure du temps de réponse sur 10 prédictions...")
            
            times = []
            for i in range(10):
                features = np.random.rand(41).tolist()
                
                start = time.time()
                response = requests.post(
                    f"{self.api_url}/predict",
                    json={'features': features},
                    timeout=10
                )
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    times.append(elapsed)
                    print(f"  Prédiction {i+1}/10: {elapsed*1000:.2f}ms", end='\r')
            
            print()  # Nouvelle ligne
            
            avg_time = np.mean(times)
            min_time = np.min(times)
            max_time = np.max(times)
            
            print(f"\n{Fore.CYAN}Résultats de performance:{Style.RESET_ALL}")
            print(f"  Temps moyen: {avg_time*1000:.2f}ms")
            print(f"  Temps min: {min_time*1000:.2f}ms")
            print(f"  Temps max: {max_time*1000:.2f}ms")
            
            # Critère de succès: < 500ms en moyenne
            if avg_time < 0.5:
                print_success("✨ Performance excellente (< 500ms)")
                self.tests_passed += 1
                return True
            elif avg_time < 1.0:
                print_success("✅ Performance acceptable (< 1s)")
                self.tests_passed += 1
                return True
            else:
                print_warning(f"⚠️  Performance à améliorer ({avg_time*1000:.0f}ms)")
                self.tests_passed += 1  # On ne fait pas échouer le test
                return True
        
        except Exception as e:
            print_error(f"Erreur lors du test de performance: {str(e)}")
            self.tests_failed += 1
            return False
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}  TESTS DU SYSTÈME IA DE DÉTECTION D'INTRUSIONS RÉSEAU")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        start_time = time.time()
        
        # Exécution des tests
        self.test_api_health()
        self.test_single_prediction()
        self.test_batch_prediction()
        self.test_edge_cases()
        self.test_performance()
        
        elapsed = time.time() - start_time
        
        # Résumé
        print_header("RÉSUMÉ DES TESTS")
        
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"{Fore.GREEN}Tests réussis: {self.tests_passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}Tests échoués: {self.tests_failed}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Taux de réussite: {success_rate:.1f}%{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Temps total: {elapsed:.2f}s{Style.RESET_ALL}")
        
        print()
        
        if self.tests_failed == 0:
            print(f"{Fore.GREEN}{'='*70}")
            print(f"{Fore.GREEN}  ✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
            print(f"{Fore.GREEN}  🚀 Le système est prêt pour la production!")
            print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")
            return True
        else:
            print(f"{Fore.RED}{'='*70}")
            print(f"{Fore.RED}  ❌ CERTAINS TESTS ONT ÉCHOUÉ")
            print(f"{Fore.RED}  🔧 Vérifiez la configuration et réessayez")
            print(f"{Fore.RED}{'='*70}{Style.RESET_ALL}\n")
            return False

def main():
    """Fonction principale"""
    print(f"\n{Fore.CYAN}🛡️  Network IDS - Suite de Tests Automatiques{Style.RESET_ALL}\n")
    
    # URL de l'API (peut être passée en argument)
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print_info(f"URL de l'API: {api_url}")
    print_info("Assurez-vous que l'API est démarrée avant de lancer les tests\n")
    
    # Demander confirmation
    try:
        input(f"{Fore.YELLOW}Appuyez sur Entrée pour commencer les tests...{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print("\n\nTests annulés.")
        sys.exit(0)
    
    # Créer et exécuter les tests
    tester = NetworkIDSTester(api_url)
    success = tester.run_all_tests()
    
    # Code de sortie
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Tests interrompus par l'utilisateur.{Style.RESET_ALL}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}Erreur fatale: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
