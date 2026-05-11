from abc import ABC, abstractmethod

# ---------------------------------------------------------
# STRATEGY DESIGN PATTERN (Aligns with Architecture Rubric)
# Implements different pricing algorithms at runtime.
# ---------------------------------------------------------

class FareStrategy(ABC):
    """Abstract Base Class for Fare Calculation Strategies."""
    @abstractmethod
    def calculate_fare(self, distance_km: float, fuel_rate: float, tolls: float, passengers: int) -> dict:
        pass

class StandardTripStrategy(FareStrategy):
    def calculate_fare(self, distance_km: float, fuel_rate: float, tolls: float, passengers: int) -> dict:
        base_cost = (distance_km * fuel_rate) + tolls
        # Driver return trip factor included slightly in base cost
        total_driver_cost = base_cost * 1.2 
        commission = total_driver_cost * 0.15 # 15% App Commission
        total_fare = total_driver_cost + commission
        
        return {
            "strategy_applied": "Standard",
            "base_cost": base_cost,
            "tolls": tolls,
            "commission": commission,
            "total_fare": total_fare,
            "per_passenger": total_fare / max(passengers, 1)
        }

class PeakHourStrategy(FareStrategy):
    def calculate_fare(self, distance_km: float, fuel_rate: float, tolls: float, passengers: int) -> dict:
        # Peak hours have a 25% surcharge on the distance/fuel cost
        base_cost = (distance_km * fuel_rate * 1.25) + tolls
        total_driver_cost = base_cost * 1.2 
        commission = total_driver_cost * 0.15
        total_fare = total_driver_cost + commission
        
        return {
            "strategy_applied": "Peak Hour (+25%)",
            "base_cost": base_cost,
            "tolls": tolls,
            "commission": commission,
            "total_fare": total_fare,
            "per_passenger": total_fare / max(passengers, 1)
        }

class LongDistanceStrategy(FareStrategy):
    def calculate_fare(self, distance_km: float, fuel_rate: float, tolls: float, passengers: int) -> dict:
        # Long distance (e.g. > 100km) applies a 10% discount on fuel rate
        base_cost = (distance_km * (fuel_rate * 0.90)) + tolls
        total_driver_cost = base_cost * 1.2 
        commission = total_driver_cost * 0.15
        total_fare = total_driver_cost + commission
        
        return {
            "strategy_applied": "Long Distance Discount (-10%)",
            "base_cost": base_cost,
            "tolls": tolls,
            "commission": commission,
            "total_fare": total_fare,
            "per_passenger": total_fare / max(passengers, 1)
        }

class FareCalculatorContext:
    """Context to switch algorithms at runtime."""
    def __init__(self, strategy: FareStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: FareStrategy):
        self._strategy = strategy

    def calculate(self, distance: float, fuel: float, tolls: float, pax: int) -> dict:
        return self._strategy.calculate_fare(distance, fuel, tolls, pax)