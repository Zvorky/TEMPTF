# Simulate Sensor MQTT Communication

'''
This script publishes random temperature readings (in a specified range) to the MQTT broker.
It is intended for testing the central server at `server/` without needing physical sensors.
'''

import argparse
import random
import time

import paho.mqtt.client as mqtt


def parse_args():
    parser = argparse.ArgumentParser(description="Simulate a sensor publishing temperature via MQTT")
    parser.add_argument("--broker", default="localhost", help="MQTT broker IPv4/host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--sensor-id", default="sim_python", help="Sensor-Device identifier")
    parser.add_argument("--interval", type=float, default=5.0, help="Interval between readings (s)")
    parser.add_argument("--min", dest="temp_min", type=float, default=18.0, help="Minimum temperature (°C)")
    parser.add_argument("--max", dest="temp_max", type=float, default=32.0, help="Maximum temperature (°C)")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.temp_min > args.temp_max:
        raise ValueError("--min cannot be greater than --max")

    topic = f"sensors/{args.sensor_id}"
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.broker, args.port, keepalive=60)
    client.loop_start()

    print(f"Publishing to {topic} on broker {args.broker}:{args.port} every {args.interval:.1f}s")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            temp_c = random.uniform(args.temp_min, args.temp_max)
            payload = str(int(round(temp_c * 100)))
            client.publish(topic, payload=payload, qos=0, retain=False)
            print(f"temp={temp_c:.2f}°C payload='{payload}'")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
