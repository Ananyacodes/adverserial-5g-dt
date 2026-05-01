class RSRPPoisonAttack:
    def __init__(self, strength_db=10):
        self.strength_db = strength_db
    
    def apply(self, telemetry_df):
        """Subtract strength_db from all RSRP values"""
        poisoned = telemetry_df.copy()
        poisoned['rsrp'] = poisoned['rsrp'] - self.strength_db
        return poisoned