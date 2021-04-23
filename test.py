from Oximeter.Core import OximeterCore
# from Oximeter.Core import OximeterDevice


def callback(device, count):
    data = []
    (count, data) = device.read(count)
    print("------")
    print(count)
    print(data)

core = OximeterCore()
devices = core.find_devices()
if len(devices) > 0:
    device = devices[0]
    device.open()
    device.set_callback(callback)
    device.start()

#
# device = OximeterDevice("aaa")
# device.set_callback(callback)
# device.start()
#
