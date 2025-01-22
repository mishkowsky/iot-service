from loguru import logger
from data_simulator.simulator import DeviceSimulator

MAX_DEVICES_COUNT = 100


class DeviceManager:

    def __init__(self, device_count: int = 0, delay: float = 30):
        self.devices: list[DeviceSimulator] = []
        for i in range(1, MAX_DEVICES_COUNT + 1):
            self.devices.append(DeviceSimulator(i, delay))
        self.active_device_count = 0
        self.update_terminating(device_count, delay)
        # self.update_device_count(device_count)
        self.delay = delay

    # def update_device_count(self, new_count: int):
    #     logger.debug(f'UPDATING ON INIT {new_count}')
    #     delta = new_count - self.active_device_count
    #     if delta > 0:
    #         self.run_devices(delta)
    #     elif delta < 0:
    #         self.stop_devices(-delta)
    #     self.active_device_count = new_count

    # def stop_devices(self, count: int):
    #     logger.debug(f'STOPPING {count} DEVICES')
    #     for device in self.devices:
    #         if count == 0:
    #             return
    #         if device.active:
    #             device.active = False
    #             logger.debug(f'DEVICE {device.device_id} ACTIVE IS {device.active}')
    #             count -= 1
    #
    # def run_devices(self, count: int):
    #     logger.debug(f'STARTING {count} DEVICES')
    #     for device in self.devices:
    #         if count == 0:
    #             return
    #         if not device.active:
    #             if device.process is not None:
    #                 device.process.terminate()
    #             device.run()
    #             count -= 1

    # def update_delay(self, new_delay: float):
    #     for device in self.devices:
    #         device.delay = new_delay

    def update_terminating(self, new_device_count: int, new_delay: float):
        logger.debug(f'UPDATING {new_device_count} {new_delay}')

        self.active_device_count = new_device_count
        self.delay = new_delay

        self.terminate_all()
        for device in self.devices:
            device.delay = new_delay
            if new_device_count != 0:
                device.run()
                new_device_count -= 1

        logger.debug(f'AAAAA {new_device_count} DEVICE COUNT NOW: {self.active_device_count}')

    def terminate_all(self):
        for device in self.devices:
            if device.process is not None:
                device.process.terminate()


if __name__ == '__main__':
    print('hello')
