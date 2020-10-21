import sys
import time

from arena_api.enums import PixelFormat
from arena_api.system import system

INTERVAL = 1


class ToFCamera():

    def __init__(self, model):
        device_infos = self.find_device_info_from_model(model)
        if device_infos:
            devices = self.create_devices_with_tries(device_infos)
        else:
            raise RuntimeError(f'not found camera model {model}')

        self.camera = devices[0]

    def find_device_info_from_model(self, model):
        device_infos = system.device_infos
        for dev in device_infos:
            if dev['model'] == model:
                return dev

    def create_devices_with_tries(self, device_info):
        tries = 0
        tries_max = 1
        sleep_time_secs = 10
        while tries < tries_max:  # Wait for device for 60 seconds
            devices = system.create_device(device_info)
            if not devices:
                print(
                    f'Try {tries+1} of {tries_max}: waiting for {sleep_time_secs} '
                    f'secs for a device to be connected!')
                for sec_count in range(sleep_time_secs):
                    time.sleep(1)
                    print(f'{sec_count + 1 } seconds passed ',
                          '.' * sec_count, end='\r')
                tries += 1
            else:
                print(f'Created {len(devices)} device(s)')
                return devices
        else:
            raise Exception('No device found! Please connect a device and run '
                            'the example again.')

    def start_stream(self, server):
        nodemap = self.camera.nodemap
        # set nodes
        pixel_format = PixelFormat.Coord3D_ABC16
        nodemap.get_node('PixelFormat').value = pixel_format
        nodemap['Scan3dOperatingMode'].value = 'Distance1500mm'
        # number of images to accumulate
        nodemap['Scan3dImageAccumulation'].value = 3
        # near mode : Exp250Us, Exp1000Us
        # nodemap['ExposureTimeSelector'].value = 'Exp1000Us'
        nodemap['ExposureTimeSelector'].value = 'Exp250Us'

        # Grab buffers ---------------------------------------------
        # Starting the stream allocates buffers
        # and begins filling them with data.
        while True:
            try:
                with self.camera.start_stream(10):
                    start = time.time()
                    buffer = self.camera.get_buffer(1)

                    # channels_pre_pixel = int(buffer.bits_per_pixel / 16)
                    # total_number_of_channels = buffer.width * buffer.height * channels_pre_pixel
                    server.save_and_update_point_cloud(buffer)
                    elapsed_time = time.time() - start
                    print(elapsed_time)

                    # Requeue the chunk data buffers
                    self.camera.requeue_buffer(buffer)
                    time.sleep(INTERVAL)
            except Exception as e:
                print(str(e))
                sys.exit(1)
                # break

        system.destroy_device()
