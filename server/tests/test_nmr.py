import pytest

from src.nmr import NMR


def _cycle(nmr: NMR, values: dict[str, int]) -> int | None:
    for sensor_id, raw in values.items():
        nmr.update_sensor(sensor_id, raw)
    return nmr.get_value()


def _make_default_nmr() -> NMR:
	return NMR(
		tolerance=10,
		isolation_steps=3,
		recovery_steps=3,
		failsafe=9999,
		verbose=False,
		stale_timeout_seconds=12,
	)


def test_nmr_exposes_state_and_last_safe_templates():
    nmr = _make_default_nmr()

    assert nmr.get_state() == "NORMAL"
    assert nmr.get_last_safe() == 9999


def test_three_sensor_consensus_immediate_with_armed_counters():
	nmr = _make_default_nmr()

	value = _cycle(nmr, {"s1": 2300, "s2": 2200, "s3": 2250})
	assert nmr.get_state() == "CONSENSUS"
	assert value == 2200
	assert nmr.get_last_safe() == 2200


def test_returns_failsafe_when_all_sensors_are_isolated():
	nmr = _make_default_nmr()
	nmr.update_sensor("s1", 2300)
	nmr.update_sensor("s2", 2200)
	nmr.sensor_data["s1"].isolate()
	nmr.sensor_data["s2"].isolate()

	value = nmr.get_value()

	assert value == 9999
	assert nmr.get_state() == "UNSTABLE"


def test_vote_cycle_updates_agree_count_for_each_sensor():
	nmr = NMR(tolerance=10, isolation_steps=3, recovery_steps=3, failsafe=None, verbose=False)

	_cycle(nmr, {"a": 10000, "b": 10000, "c": 12000})

	assert nmr.sensor_data["a"].get_agree_count() == 1
	assert nmr.sensor_data["b"].get_agree_count() == 1
	assert nmr.sensor_data["c"].get_agree_count() == -1


def test_sensor_isolated_after_three_consecutive_disagreements():
	nmr = NMR(tolerance=10, isolation_steps=3, recovery_steps=3, failsafe=None, verbose=False)

	_cycle(nmr, {"a": 10000, "b": 10000, "c": 12000})
	_cycle(nmr, {"a": 10010, "b": 10000, "c": 12020})
	_cycle(nmr, {"a": 10000, "b": 10020, "c": 12100})

	assert nmr.sensor_data["c"].is_isolated() is True
	assert nmr.sensor_data["c"].get_agree_count() == 0


def test_state_transitions_to_degraded_with_one_sensor_isolated():
	nmr = NMR(tolerance=10, isolation_steps=3, recovery_steps=3, failsafe=None, verbose=False)

	_cycle(nmr, {"a": 10000, "b": 10000, "c": 12000})
	_cycle(nmr, {"a": 10000, "b": 10010, "c": 12010})
	_cycle(nmr, {"a": 10020, "b": 10000, "c": 12020})

	assert nmr.sensor_data["c"].is_isolated() is True
	_cycle(nmr, {"a": 10000, "b": 10000, "c": 12000})
	_cycle(nmr, {"a": 10000, "b": 10005, "c": 12000})
	_cycle(nmr, {"a": 10001, "b": 10000, "c": 12000})

	assert nmr.get_state() == "DEGRADED"


def test_unstable_returns_last_safe_for_two_active_sensors_in_divergence():
	nmr = _make_default_nmr()

	# Build a stable last safe value.
	safe = _cycle(nmr, {"a": 10000, "b": 10000, "c": 10010})
	assert safe is not None

	# Isolate c.
	_cycle(nmr, {"a": 10000, "b": 10000, "c": 12000})
	_cycle(nmr, {"a": 10010, "b": 10000, "c": 12000})
	_cycle(nmr, {"a": 10000, "b": 10020, "c": 12000})
	assert nmr.sensor_data["c"].is_isolated() is True

	# Remaining active sensors diverge by > 10%.
	result = _cycle(nmr, {"a": 10000, "b": 12000, "c": 12000})

	assert nmr.get_state() == "UNSTABLE"
	assert result == safe


def test_isolated_sensor_recovers_after_three_consecutive_agreements():
	nmr = NMR(tolerance=10, isolation_steps=3, recovery_steps=3, failsafe=None, verbose=False)

	# Isolate c first.
	_cycle(nmr, {"a": 10000, "b": 10000, "c": 12000})
	_cycle(nmr, {"a": 10010, "b": 10000, "c": 12000})
	_cycle(nmr, {"a": 10000, "b": 10020, "c": 12100})
	assert nmr.sensor_data["c"].is_isolated() is True

	# Then feed c with values in agreement.
	_cycle(nmr, {"a": 10000, "b": 10000, "c": 10010})
	_cycle(nmr, {"a": 10000, "b": 10010, "c": 10000})
	_cycle(nmr, {"a": 10010, "b": 10000, "c": 10000})

	assert nmr.sensor_data["c"].is_isolated() is False
	assert nmr.sensor_data["c"].get_agree_count() == 0


def test_masked_failure_state_when_one_of_three_active_disagrees():
	nmr = NMR(tolerance=10, isolation_steps=3, recovery_steps=3, failsafe=None, verbose=False)

	value = _cycle(nmr, {"a": 10000, "b": 10000, "c": 13000})

	assert nmr.get_state() == "MASKED_FAILURE"
	assert value == 10000
	assert nmr.get_last_safe() == 10000


def test_no_data_state_after_sensor_timeout_uses_last_safe():
	nmr = _make_default_nmr()
	safe = _cycle(nmr, {"a": 10000, "b": 10000, "c": 10000})
	assert safe == 10000

	for sensor in nmr.sensor_data.values():
		sensor.last_update -= 1000

	value = nmr.get_value()
	assert nmr.get_state() == "NO_DATA"
	assert value == 10000


def test_single_active_sensor_without_last_safe_returns_sensor_value():
	nmr = NMR(tolerance=10, isolation_steps=3, recovery_steps=3, failsafe=None, verbose=False)
	nmr.update_sensor("a", 1234)

	value = nmr.get_value()

	assert nmr.get_state() == "UNSTABLE"
	assert value == 1234
