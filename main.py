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

RGB_OFF: tuple[int, int, int] = (0, 0, 0)
RED: tuple[int, int, int] = (255, 0, 0)
GREEN: tuple[int, int, int] = (0, 255, 0)
PURPLE: tuple[int, int, int] = (255, 0, 255)

rgb_led: NeoPixel = NeoPixel(Pin(48), 1)
uv_led: Pin = Pin(5, Pin.OUT)


def toggle_pin(pin: Pin) -> None:
    """*Toggle specific pin on ESP32*.

    Args:
        pin (Pin): *Numbered pin*

    """
    pin.value(not pin.value())


def set_rgb_led(
    color: tuple[int, int, int],
    seconds: float = 0,
    pulse: int = 0,
) -> None:
    """*Set ESP32 RGB LED to a certain color*.

    Args:
        color (tuple[int, int, int]): *Specified color*
        seconds (float, optional): *Turn off after waiting*. Defaults to 0.
        pulse (int, optional): *# of pulses*. Defaults to 0.

    """
    rgb_led[0] = RGB_OFF
    rgb_led.write()
    if not seconds:
        rgb_led[0] = color
        rgb_led.write()
    elif not pulse:
        sleep(seconds)
        rgb_led[0] = RGB_OFF
        rgb_led.write()
    for _ in range(pulse):
        rgb_led[0] = color
        rgb_led.write()
        sleep(seconds)
        rgb_led[0] = RGB_OFF
        rgb_led.write()
        sleep(seconds)


def connect_wifi(ssid: str, password: str) -> None:
    """*Connect ESP32 to a specified Wi-Fi network*.

    Args:
        ssid (str): *SSID*
        password (str): *Password*

    """
    wlan: network.WLAN = network.WLAN(network.STA_IF)
    wlan.active(WIFI_OFF)
    sleep(0.1)
    wlan.active(WIFI_ON)
    sleep(0.1)
    print("Connecting...")
    set_rgb_led(RED, seconds=2.0)
    wlan.connect(ssid, password)
    sleep(1)
    print("Connected! IP:", wlan.ifconfig()[0])
    set_rgb_led(GREEN, seconds=2.0)


def disconnect_wifi() -> None:
    """*Disconnect ESP32 from current Wi-Fi network*."""
    wlan: network.WLAN = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        print("Disconnecting...")
        set_rgb_led(RED, seconds=0.1, pulse=5)
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
        uv_led.on()
        print("LED: On")
    elif msg == b"OFF":
        uv_led.off()
        print("LED: Off")
    elif msg == b"filler":
        toggle_pin(uv_led)


def main() -> None:
    """*Control ESP32*."""
    uv_led.off()
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



