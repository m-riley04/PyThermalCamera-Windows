import io

def is_raspberrypi():
    """
    Checks if we're running on a Raspberry Pi by reading the device model from the system's device tree.
    Taken from the original repo from Les Wright.
    """
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass # TODO: catch specific exceptions?
    return False