# ruff: ignore[CPY001]
"""*Main Python script*."""

from time import sleep

import network
from machine import Pin
from neopixel import NeoPixel
from umqtt.simple import MQTTClient

R2_SSID: str = "Adams County Mosque"
R2_KEY: str = "allahuakbar777"

MQTT_CLIENT_ID: str = "esp32s3_client_hackohio2026"
MQTT_SERVER: str = "broker.hivemq.com"
MQTT_TOPIC: str = "myhome/esp32s3/led"

WIFI_ON: bool = True
WIFI_OFF: bool = False

LED_OFF: tuple[int, int, int] = (0, 0, 0)
RED: tuple[int, int, int] = (255, 0, 0)
GREEN: tuple[int, int, int] = (0, 255, 0)
PURPLE: tuple[int, int, int] = (255, 0, 255)


def set_led(
    rgb: tuple[int, int, int],
    seconds: float = 0,
    pulse: int = 0,
) -> None:
    """*Set ESP32 LED to a certain color*.

    Args:
        rgb (tuple[int, int, int]): *Specified color*
        seconds (float, optional): *Turn off after waiting*. Defaults to 0.
        pulse (int, optional): *# of pulses*. Defaults to 0.

    """
    led: NeoPixel = NeoPixel(Pin(48), 1)
    if not seconds:
        led[0] = rgb
        led.write()
        return
    for _ in range(pulse + 1):
        led[0] = rgb
        led.write()
        sleep(seconds)
        led[0] = (0, 0, 0)
        led.write()
        sleep(seconds)


def connect_wifi(ssid: str, password: str) -> None:
    """*Connect ESP32 to a specified Wi-Fi network*.

    Args:
        ssid (str): *SSID*
        password (str): *Password*

    """
    wlan: network.WLAN = network.WLAN(network.STA_IF)
    wlan.active(WIFI_ON)
    print("Connecting...")
    set_led(RED, seconds=1.0)
    wlan.connect(ssid, password)
    print("Connected! IP:", wlan.ifconfig()[0])
    set_led(GREEN, seconds=1.0)


def disconnect_wifi() -> None:
    """*Disconnect ESP32 from current Wi-Fi network*."""
    wlan: network.WLAN = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        print("Disconnecting...")
        set_led(RED, seconds=0.2, pulse=5)
        wlan.disconnect()
        wlan.active(WIFI_OFF)
        print("Disconnected!")
    else:
        print("Wi-Fi was not connected.")


def msg_to_cmd(topic: bytes, msg: bytes) -> None:
    """*Use website message to command ESP32*.

    Args:
        topic (bytes): *Received topic*
        msg (bytes): *Topic message*

    """
    print(f"Received message on {topic.decode()}: {msg.decode()}")
    if msg == b"ON":
        set_led(PURPLE)
        print("LED: On")
    elif msg == b"OFF":
        set_led(LED_OFF)
        print("LED: Off")


def main() -> None:
    """*Control ESP32*."""
    connect_wifi(R2_SSID, R2_KEY)

    client: MQTTClient = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER)
    client.set_callback(msg_to_cmd)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print(f"Connected to MQTT broker and subscribed to {MQTT_TOPIC}")

    try:
        while True:
            client.check_msg()
            sleep(0.1)
    except KeyboardInterrupt:
        client.disconnect()
    finally:
        disconnect_wifi()


if __name__ == "__main__":
    main()
