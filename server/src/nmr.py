# TEMPTF - N Modular Redundancy (NMR)


class SensorData:
    def __init__(self, raw_value : int, factor: float = 1.0, offset: int = 0):
        self.factor = factor       # Factor to multiply raw value; Affects get_value()
        self.offset = offset       # Offset to add to the scaled value; Affects get_value()
        self.raw_value = raw_value # Raw value from the sensor
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
    def __init__(self, tolerance: int = 10, isolation_steps: int = 3, recovery_steps: int = 3, failsafe: int | None = None, verbose = True):
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

    def update_sensor(self, sensor_id: str, raw_value: int):
        if sensor_id not in self.sensor_data:
            self.sensor_data[sensor_id] = SensorData(raw_value)
        else:
            self.sensor_data[sensor_id].update(raw_value)

    # NMR Voter Logic
    def get_value(self) -> int | None:
        ''' Return the minimum value of active sensors in consensus '''
        active_sensors = []
        isolated_sensors = []

        for sensor_id, data in self.sensor_data.items():
            is_isolated = data.is_isolated()
            if is_isolated:
                isolated_sensors.append((sensor_id, data))
            else:
                active_sensors.append((sensor_id, data))
            if self.verbose:
                print(f"Sensor {sensor_id} {"[ISOLATED]" if is_isolated else "[ACTIVE]"}: Value={data.get_value()} AgreeCount={data.get_agree_count()}")

        if not active_sensors:
            return self.failsafe

        values = [s.get_value() for _, s in active_sensors]
        return min(values)