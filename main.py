# ruff: ignore[CPY001]
"""*Main Python script*."""

import sys
import time

import network
from machine import ADC, I2C, Pin
from neopixel import NeoPixel
from umqtt.simple import MQTTClient
from vl53l0x import VL53L0X

CLEAR_TERMINAL: str = "\033[2J\033[H"

HOTSPOT: dict[str, str] = {
    "ssid": "Adams County Mosque",
    "key": "allahuakbar777",
}

MQTT: dict[str, str] = {
    "client_id": "esp32s3_client_hackohio2026",
    "server": "broker.hivemq.com",
    "topic": "myhome/esp32s3/led",
}

WIFI: dict[str, bool] = {
    "on": True,
    "off": False,
}

COLOR: dict[str, tuple[int, int, int]] = {
    "off": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
}

PIN: dict[str, int] = {
    "rgb": 48,
    "uv": 6,
    "dist_clock": 9,
    "dist_data": 8,
    "ldr_1": 4,
    "ldr_2": 5,
    "pressure": 1,
}


# rgb_led: NeoPixel = NeoPixel(Pin(PIN["rgb"]), 1)
uv_led: Pin = Pin(PIN["uv"], Pin.OUT)
# distance: VL53L0X = VL53L0X(
#     I2C(
#         0,
#         scl=Pin(PIN["dist_clock"]),
#         sda=Pin(PIN["dist_data"]),
#         freq=100_000,
#     ),
# )
ldr_1: ADC = ADC(Pin(PIN["ldr_1"]))
ldr_2: ADC = ADC(Pin(PIN["ldr_2"]))
pressure: ADC = ADC(Pin(PIN["pressure"]))

for sensor in (ldr_1, ldr_2, pressure):
    sensor.atten(ADC.ATTN_11DB)


def toggle_uv_led() -> None:
    """*Toggle UV LED*."""
    uv_led.value(not uv_led.value())


# def _send_color(color: tuple[int, int, int]) -> None:
#     rgb_led[0] = color
#     rgb_led.write()


# def _disable_rgb_led() -> None:
#     _send_color(COLOR["off"])


# def set_rgb_led(
#     color: tuple[int, int, int],
#     seconds: float = 0,
#     pulse: int = 0,
# ) -> None:
#     """*Set ESP32 RGB LED to a certain color*.

#     Args:
#         color (tuple[int, int, int]): *Specified color*
#         seconds (float, optional): *Turn off after waiting*. Defaults to 0.
#         pulse (int, optional): *# of pulses*. Defaults to 0.

#     """
#     if rgb_led[0] != COLOR["off"]:
#         _disable_rgb_led()
#     if not seconds:
#         _send_color(color)
#     elif not pulse:
#         time.sleep(seconds)
#         _disable_rgb_led()
#     for _ in range(pulse):
#         _send_color(color)
#         time.sleep(seconds)
#         _disable_rgb_led()
#         time.sleep(seconds)


# def read_distance_sensor() -> int:
#     return distance.read_range_single_millimeters()


def _print_ellipsis() -> None:
    for _ in range(3):
        print(".", end="")
        time.sleep(0.15)


def wait_display() -> None:
    """*Show "loading" ellipsis*."""
    for _ in range(3):
        _print_ellipsis()
        sys.stdout.write("\b\b\b   \b\b\b")
    _print_ellipsis()


def connect_wifi(ssid: str, password: str) -> None:
    """*Connect ESP32 to a specified Wi-Fi network*.

    Args:
        ssid (str): *SSID*
        password (str): *Password*

    """
    wlan: network.WLAN = network.WLAN(network.STA_IF)
    wlan.active(WIFI["off"])
    time.sleep(0.1)
    wlan.active(WIFI["on"])
    time.sleep(0.1)
    print("Connecting to Wi-Fi", end="")
    # set_rgb_led(COLOR["red"], seconds=2.0)
    wlan.connect(ssid, password)
    wait_display()
    time.sleep(1)
    print("\nConnected to Wi-Fi! IP:", wlan.ifconfig()[0])
    # set_rgb_led(COLOR["green"], seconds=2.0)


def disconnect_wifi() -> None:
    """*Disconnect ESP32 from current Wi-Fi network*."""
    wlan: network.WLAN = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        print("Disconnecting from Wi-Fi", end="")
        wait_display()
        # set_rgb_led(COLOR["red"], seconds=0.1, pulse=5)
        wlan.disconnect()
        wlan.active(WIFI["off"])
        print("\nDisconnected from Wi-Fi!")
    else:
        print("Wi-Fi was not connected.")


def msg_to_cmd(topic: bytes, msg: bytes) -> None:
    """*Use website message to command ESP32*.

    Args:
        topic (bytes): *Received topic*
        msg (bytes): *Topic message*

    """
    if msg == b"toggle":
        toggle_uv_led()


def main() -> None:
    """*Control ESP32*."""
    uv_led.off()
    connect_wifi(HOTSPOT["ssid"], HOTSPOT["key"])

    client: MQTTClient = MQTTClient(MQTT["client_id"], MQTT["server"])
    print("Connecting to MQTT broker", end="")
    wait_display()
    print("\nConnected to MQTT broker!")
    client.set_callback(msg_to_cmd)
    print(f"Subscribing to {MQTT['topic']}", end="")
    client.connect()
    wait_display()
    time.sleep(1)
    client.subscribe(MQTT["topic"])
    print(f"\nSubscribed to {MQTT['topic']}!")
    time.sleep(2)

    try:
        sys.stdout.write(CLEAR_TERMINAL)
        while True:
            client.check_msg()
            time.sleep(0.1)
            sys.stdout.write("\033[H")
            # sys.stdout.write(f"Distance: {read_distance_sensor():<10} mm\n")
            sys.stdout.write(f"LDR 1: {ldr_1.read():<4} ohms\n")
            sys.stdout.write(f"LDR 2: {ldr_2.read():<4} ohms\n")
            sys.stdout.write(
                f"Pressure Resistance: {pressure.read():<4} ohms\n",
            )
            sys.stdout.write(f"LED Indicator: {uv_led.value():<1}\n")
            time.sleep(0.2)
    except KeyboardInterrupt:
        sys.exit()
    except OSError as e:
        sys.exit(e)
    finally:
        client.disconnect()
        disconnect_wifi()


if __name__ == "__main__":
    main()
