# Intruder Alert

**Name:** Denis Grinevicius 
**Student ID:** D00283068 
**GitHub:** https://github.com/Denisgri109/IntruderAlert

---

## What is this?
This is a college IoT project where I built a intruder alert system. Basically, it's designed to keep an eye on a room during specific hours (like when you're sleeping or away) and alert you if someone sneaks in. It connects to a web dashboard where you can control the settings and see what's happening in real-time.

## Parts Used
**Hardware:**
*   **Raspberry Pi:** The brain of the operation.
*   **PIR Motion Sensor:** To detect if someone is moving around.
*   **LDR Light Sensor:** To detect changes in light (like someone turning on a lamp or using a flashlight).
*   **Active Buzzer:** For the loud alarm sound.
*   **LEDs:** For visual alerts (like a flashing light when the alarm goes off).

**Software/Tech Stack:**
*   **Python:** Runs the logic on the Raspberry Pi to read sensors and control components.
*   **FastAPI:** Powers the backend API and web interface.
*   **SQLite:** A lightweight database to store user logins, schedules, and alert logs.

## How It Works
1. **The Web Dashboard:** You log into the website and set a schedule for when the alarm should be active (for example, from 10:00 PM to 5:00 AM). 
2. **Motion Detected:** If the alarm is "armed" and the PIR sensor picks up movement, the system goes into full panic mode. It automatically sounds the buzzer, flashes the LED, and sends an alert straight to the website.
3. **Light Detected (No Motion):** If the LDR sensor detects a sudden change in light, but there's no movement (maybe someone shined a flashlight through the window or flipped a switch from the doorway), it handles things differently. Instead of sounding the alarm right away, it sends a *silent warning* to the web dashboard. From there, you can see the alert and click a button to manually trigger the buzzer if you want to.

## Setup & Running the Project
1. Clone this repository.
2. Run the FastAPI server.
3. Run the main Raspberry Pi script. 
