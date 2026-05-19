# TEMPTF - N Modular Redundancy (NMR)

import logging
import time


class SensorData:
    def __init__(self, raw_value : int, factor: float = 1.0, offset: int = 0):
        self.factor = factor       # Factor to multiply raw value; Affects get_value()
        self.offset = offset       # Offset to add to the scaled value; Affects get_value()
        self.raw_value = raw_value # Raw value from the sensor
        self.last_update = time.time()  # Last update timestamp
        self._isolated = False     # Whether the sensor is currently isolated due to disagreement
        self._agree_count = 0      # Consecutive agreements/disagreements; Negative = Disagreements

    def get_value(self) -> int:
        ''' Get the calibrated value '''
        return int(self.raw_value * self.factor + self.offset)

    def get_agree_count(self) -> int:
        return self._agree_count

    def is_isolated(self) -> bool:
        return self._isolated

    def update(self, raw_value: int):
        ''' Update the raw value from the sensor '''
        self.raw_value = raw_value
        self.last_update = time.time()

    def tune(self, factor: float | None = None, offset: int | None = None):
        '''
            factor: Multiplier for the raw value (e.g., 1.05 to increase by 5%)
            offset: Value to add to the scaled value (e.g., -2 to decrease by 2 degrees)
        '''
        if factor is not None:
            self.factor = factor
        if offset is not None:
            self.offset = offset

    def update_agreement(self, agrees: bool):
        if self._agree_count and agrees == (self._agree_count < 0):
            self._agree_count = 0
        self._agree_count += 1 if agrees else -1

    def isolate(self):
        self._isolated = True
        self._agree_count = 0

    def recover(self):
        self._isolated = False
        self._agree_count = 0


class NMR:
    def __init__(
        self,
        tolerance: int = 10,
        isolation_steps: int = 3,
        recovery_steps: int = 3,
        failsafe: int | None = None,
        verbose: bool = True,
        stale_timeout_seconds: int = 12,
        logger: logging.Logger | None = None,
    ):
        '''
            Tolerance in percentage for considering values as agreeing
            Isolation steps: number of consecutive disagreements before isolating a sensor
            Recovery steps: number of consecutive agreements before recovering an isolated sensor
        '''
        self.sensor_data = {}
        self.tolerance = tolerance
        self.isolation_steps = isolation_steps
        self.recovery_steps = recovery_steps
        self.failsafe = failsafe
        self.verbose = verbose
        self.stale_timeout_seconds = stale_timeout_seconds
        self.logger = logger or logging.getLogger("temptf.nmr")
        self._state = "NORMAL"
        self._last_safe = failsafe
        self._degraded_agree_cycles = 3
        self._consensus_agree_cycles = 3

    def get_state(self) -> str:
        return self._state

    def get_last_safe(self) -> int | None:
        return self._last_safe

    def update_sensor(self, sensor_id: str, raw_value: int):
        if sensor_id not in self.sensor_data:
            self.sensor_data[sensor_id] = SensorData(raw_value)
        else:
            self.sensor_data[sensor_id].update(raw_value)

    def tune_sensor(self, sensor_id: str, factor: float | None = None, offset: int | None = None):
        if sensor_id not in self.sensor_data:
            self.logger.warning("Sensor \"%s\" not registered yet, setting it anyway...", sensor_id)
            self.sensor_data[sensor_id] = SensorData(0)
        self.sensor_data[sensor_id].tune(factor, offset)

    def _within_tolerance(self, a: int, b: float) -> bool:
        if b == 0:
            return a == 0
        return abs(a - b) / abs(b) * 100 <= self.tolerance

    def _alive_sensors(self) -> dict[str, SensorData]:
        now = time.time()
        return {
            sensor_id: data
            for sensor_id, data in self.sensor_data.items()
            if (now - data.last_update) < self.stale_timeout_seconds
        }

    def _log_sensor_status(self, alive_sensors: dict[str, SensorData]) -> None:
        if not self.verbose:
            return
        for sensor_id, data in alive_sensors.items():
            status = "ISOLATED" if data.is_isolated() else "ACTIVE"
            self.logger.info(
                "Sensor %s [%s]: Value=%s AgreeCount=%s",
                sensor_id,
                status,
                data.get_value(),
                data.get_agree_count(),
            )

    # NMR Voter Logic
    def get_value(self) -> int | None:
        '''
        Evaluate one NMR cycle and return the voted value.

        States:
            NORMAL
            RECOVERING_CONSENSUS
            CONSENSUS
            MASKED_FAILURE
            DEGRADED
            RECOVERING_DEGRADED
            UNSTABLE
            NO_DATA
        '''
        alive = self._alive_sensors()
        self._log_sensor_status(alive)

        if not alive:
            self._state = "NO_DATA"
            return self._last_safe if self._last_safe is not None else self.failsafe

        active = {sensor_id: data for sensor_id, data in alive.items() if not data.is_isolated()}
        baseline_values = [d.get_value() for d in (active.values() or alive.values())]
        baseline_mean = sum(baseline_values) / len(baseline_values)

        for data in alive.values():
            agrees = self._within_tolerance(data.get_value(), baseline_mean)
            data.update_agreement(agrees)

            if not data.is_isolated() and data.get_agree_count() <= -self.isolation_steps:
                data.isolate()
            elif data.is_isolated() and data.get_agree_count() >= self.recovery_steps:
                data.recover()

        active_values = [d.get_value() for d in alive.values() if not d.is_isolated()]

        if not active_values:
            self._degraded_agree_cycles = 0
            self._state = "UNSTABLE"
            return self._last_safe if self._last_safe is not None else self.failsafe

        if len(active_values) == 1:
            self._degraded_agree_cycles = 0
            self._state = "UNSTABLE"
            return self._last_safe if self._last_safe is not None else active_values[0]

        if len(active_values) == 2:
            self._consensus_agree_cycles = 0
            a, b = active_values

            if self._within_tolerance(a, b):
                self._degraded_agree_cycles += 1
                voted = min(active_values)
                if self._degraded_agree_cycles >= 3 or self._last_safe is None:
                    self._last_safe = voted
                    self._state = "DEGRADED"
                    return voted

                self._state = "RECOVERING_DEGRADED"
                return self._last_safe

            self._degraded_agree_cycles = 0
            self._state = "UNSTABLE"
            return self._last_safe if self._last_safe is not None else min(active_values)

        safe_values = [v for v in active_values if self._within_tolerance(v, baseline_mean)]
        voted = min(safe_values) if safe_values else min(active_values)

        if len(safe_values) == len(active_values):
            self._consensus_agree_cycles += 1
            self._degraded_agree_cycles = 3

            if self._consensus_agree_cycles >= 3 or self._last_safe is None:
                self._last_safe = voted
                self._state = "CONSENSUS"
                return voted

            self._last_safe = voted
            self._state = "RECOVERING_CONSENSUS"
            return voted

        self._consensus_agree_cycles = 0
        self._last_safe = voted
        self._state = "MASKED_FAILURE"
        return voted