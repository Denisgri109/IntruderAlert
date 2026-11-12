import asyncio
import json
import os
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


async def send_readings(websocket):
    while True:
        await websocket.send(json.dumps(read_sensors()))
        await asyncio.sleep(1)


async def main():
    while True:
        try:
            print(f"Connecting to {SERVER_URL}...")
            async with websockets.connect(SERVER_URL, additional_headers={"X-Pi-Secret": PI_SECRET_KEY}) as ws:
                print("Successfully connected to Intruder Alert backend!")
                await send_readings(ws)
        except Exception as e:
            print(f"Connection failed ({e}). Retrying in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping sensors...")
    finally:
        buzzer.off()
        alarm_led.off()
