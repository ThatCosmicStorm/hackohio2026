
import time
from machine import Pin
import network
import neopixel
from umqtt.simple import MQTTClient

SUR_SSID = "iPhone (2)"
SUR_PASSWORD = "SurIsTheBest"

JASON_SSID = "Jason wei's phone"
JASON_PASSWORD = "Wegonnawin"

MQTT_CLIENT_ID = "esp32s3_client_hackohio2026"
MQTT_SERVER = "broker.hivemq.com"
MQTT_TOPIC = "myhome/esp32s3/led"


np = neopixel.NeoPixel(Pin(48), 1)


def blink(r: int, g: int, b: int):
    np[0] = (r, g, b)
    np.write()
    time.sleep(1)
    np[0] = (0, 0, 0)
    np.write()


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        blink(50, 0, 0)
        wlan.connect(JASON_SSID, JASON_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("Connected to Wi-Fi! IP:", wlan.ifconfig()[0])
    blink(0, 50, 0)


def disconnect_wifi():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        print("Disconnecting from Wi-Fi...")
        blink(0, 50, 0)
        wlan.disconnect()
        wlan.active(False)
        print("Disconnected")
    else:
        print("Wi-Fi was not connected.")


def sub_cb(topic, msg):
    print(f"Received message on {topic.decode()}: {msg.decode()}")
    if msg == b"ON":
        blink(255, 255, 255)
        print("LED turned ON")
    elif msg == b"OFF":
        blink(0, 0, 0)
        print("LED turned OFF")


def main():
    connect_wifi()

    client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print(f"Connected to MQTT broker and subscribed to {MQTT_TOPIC}")

    try:
        while True:
            client.check_msg()
            time.sleep(.1)
    except Exception as e:
        print("Error:", e)
        client.disconnect()
    finally:
        disconnect_wifi()


if __name__ == "__main__":
    connect_wifi()
    time.sleep(5)
    disconnect_wifi()
