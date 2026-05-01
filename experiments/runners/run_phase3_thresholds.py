"""Measure minimum perturbations required to flip DT decisions"""

import itertools
from pathlib import Path
from attacks.metric_poisoning.rsrp_poison import RSRPPoisonAttack
from models.detectors.isolation_forest import IsolationForestDetector

def run_threshold_experiment():
    # Load baseline model
    detector = IsolationForestDetector()
    detector.load('models/checkpoints/isolation_forest_baseline.pkl')
    
    # Test different poison strengths
    strengths = [1, 2, 3, 5, 7, 10, 12, 15, 20]  # dB
    
    results = []
    for strength in strengths:
        # Load benign telemetry
        df = pd.read_csv(f'telemetry/raw/benign/simulation_1hour.csv')
        
        # Apply attack
        attack = RSRPPoisonAttack(strength_db=strength)
        poisoned_df = attack.apply(df)
        
        # Extract features and predict
        features = extract_features(poisoned_df)
        predictions = detector.predict(features)
        
        # Attack succeeds when detector says "normal" (0) but should be "anomaly" (1)
        # (We know ground truth: all poisoned data is anomalous)
        attack_success_rate = 1 - predictions.mean()
        
        results.append({
            'poison_strength_dB': strength,
            'attack_success_rate': attack_success_rate
        })
    
    # Save results
    pd.DataFrame(results).to_csv('experiments/results/phase3/rsrp_thresholds.csv')
    
    # Find threshold where success rate exceeds 50%
    threshold = find_knee_point(results)
    print(f"Minimum perturbation for >50% success: {threshold} dB")

if __name__ == '__main__':
    run_threshold_experiment()