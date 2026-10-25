import time

from machine import Pin


def barometer(timeout_ms: int = 1000, sleep_ms: int = 100) -> int:
    sck: Pin = Pin(4, Pin.OUT, value=0)
    dout: Pin = Pin(5, Pin.IN, Pin.PULL_UP)

    start: int = time.ticks_ms()
    while dout.value():
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            error_msg: str = "TM7711 conversion timeout"
            raise OSError(error_msg)
        time.sleep_ms(1)

    value: int = 0

    for _ in range(24):
        sck.value(1)
        time.sleep_us(2)

        value: int = (value << 1) | dout.value()

        sck.value(0)
        time.sleep_us(2)

    sck.value(1)
    time.sleep_us(2)
    sck.value(0)
    time.sleep_us(2)

    if value & 0x800000:
        value -= 0x1000000

    time.sleep_ms(sleep_ms)

    return value


def read_barom_samples() -> None:
    readings: list = [barometer() for _ in range(200)]
    print("Average:", sum(readings) / len(readings))
    print("Range:", max(readings) - min(readings))


BASE_LOW = 4_596_388
BASE_HIGH = 4_596_688


def is_barom_at_baseline(reading: int) -> bool:
    return BASE_LOW <= reading <= BASE_HIGH
