import os
import sys
from concurrent import futures
from datetime import datetime

import aion.common_library as common
import grpc
import numpy as np
import open3d as o3d
from arena_api.__future__.save import Writer

from .pcdproto import ndarray_to_proto
from .PointCloud_pb2_grpc import (MainServerServicer,
                                  add_MainServerServicer_to_server)
from .tof_camera import ToFCamera

OUTPUTPATH = common.get_output_path(os.getcwd(), __file__)
CAMERA_MODEL = 'HLS003S-001'
SEND_SIZE = 120000
UNSIGNED_16BIT_MAX = 65535


class PointCloudServer(MainServerServicer):

    def __init__(self):
        self.point_cloud = []
        self.npcd = []
        self.timestamp = ''
        self.writer = Writer()

    def get_point_cloud(self, request, context):
        total_size = self.npcd.shape[0]

        cnt = 0
        while cnt < total_size:
            if cnt + SEND_SIZE > total_size:
                _point_cloud = self.npcd[cnt:]
                point_reply = ndarray_to_proto(
                    _point_cloud, self.timestamp)
                yield point_reply
            else:
                _point_cloud = self.npcd[cnt:cnt + SEND_SIZE]
                point_reply = ndarray_to_proto(
                    _point_cloud, self.timestamp)
                yield point_reply

            print(
                f"send {len(_point_cloud)}")
            cnt += len(_point_cloud)
        print(f'send total {cnt}')

    def save_and_update_point_cloud(self, buffer):
        # write ply
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        file_path = os.path.join(OUTPUTPATH, 'pointcloud.ply')
        self.writer.save(buffer, file_path)
        # print(f'write ply to {file_path}')
        # read ply
        o3d.io.read_point_cloud(file_path)
        pcd = o3d.io.read_point_cloud(file_path)
        self.npcd = np.asarray(pcd.points, dtype=np.float32)
        self.timestamp = timestamp

    # FIXME: NOT USE THIS METHOD BECAUSE USING PLY FILE
    def update_PointCloud(self, pdata, total_number_of_channels,
                          channels_per_pixel):
        _point_cloud = []
        for i in range(0, total_number_of_channels, channels_per_pixel):
            # Extract channels from point/pixel
            #   The first channel is the x coordinate,
            #   the second channel is the y coordinate,
            #   the third channel is the z coordinate, and
            x = pdata[i]
            y = pdata[i + 1]
            z = pdata[i + 2]

            # if z is less than max value, as invalid values get
            # filtered to UNSIGNED_16BIT_MAX
            if z < UNSIGNED_16BIT_MAX:
                # Convert x, y and z to millimeters
                #   Using each coordinates' appropriate scales,
                #   convert x, y and z values to mm. For the x and y
                #   coordinates in an unsigned pixel format, we must then
                #   add the offset to our converted values in order to
                #   get the correct position in millimeters.

                x = (x * self.scale_x) + self.offset_x
                y = (y * self.scale_y) + self.offset_y
                z = z * self.scale_z
                _point_cloud.append([int(x), int(y), int(z)])

        self.point_cloud = _point_cloud
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")


def run_server(port=50051):
    # MAX_MESSAGE_SEND_SIZE = 10 * 1024 * 1024
    # options = [('grpc.max_send_message_length', MAX_MESSAGE_SEND_SIZE)]
    tof = ToFCamera(CAMERA_MODEL)
    pointcloud = PointCloudServer()
    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=10), options=[])
    add_MainServerServicer_to_server(pointcloud, server)
    server.add_insecure_port(f'[::]:{port}')
    print(f"========== server start: localhost:{port} ==============")

    server.start()

    tof.start_stream(pointcloud)
    server.wait_for_termination()
    server.stop(1)
