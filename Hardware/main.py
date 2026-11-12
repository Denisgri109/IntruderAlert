import asyncio
import json
import os
import time
import websockets
from dotenv import load_dotenv
from gpiozero import MotionSensor, MCP3008, Buzzer, LED

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")
PI_SECRET_KEY = os.getenv("PI_SECRET_KEY")

motion_sensor = MotionSensor(23)
light_sensor = MCP3008(channel=0)
buzzer = Buzzer(24, active_high=False)
alarm_led = LED(25)


def read_sensors():
    return {
        "motion": motion_sensor.is_active,
        "light_level": round(light_sensor.value, 3),
    }


def main():
    print("Checking sensors. Press Ctrl+C to stop.")
    while True:
        reading = read_sensors()
        motion_text = "yes" if reading["motion"] else "no"
        print(f"Motion: {motion_text} | Light level: {reading['light_level']}")
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping sensors...")
    finally:
        buzzer.off()
        alarm_led.off()
