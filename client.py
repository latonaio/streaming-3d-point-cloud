# ============================================================
# import packages
# ============================================================
import sys
import time
from concurrent import futures
from datetime import datetime

import grpc
import numpy as np
import open3d as o3d

from api import PointCloud_pb2, PointCloud_pb2_grpc, pcdproto

# ============================================================
# class
# ============================================================


# ============================================================
# property
# ============================================================


# ============================================================
# functions
# ============================================================
def run():
    ary = []
    res = None
    # MAX MESSAGE RECIVE SIZE
    MAX_MESSAGE_RECIVE_SIZE = 30 * 1024 * 1024
    options = [('grpc.max_receive_message_length', MAX_MESSAGE_RECIVE_SIZE)]
    with grpc.insecure_channel('localhost:50051', options=[]) as channel:
        try:
            stub = PointCloud_pb2_grpc.MainServerStub(channel)
            # return generator
            start = time.time()
            responses = stub.get_point_cloud(PointCloud_pb2.PointRequest())
            elapsed_time = time.time() - start
            print(f"grcp {elapsed_time}秒かかりました")
            # res = responses.next()
            start = time.time()
            cnt = 0
            for res in responses:
                nda = pcdproto.proto_to_ndarray(res)
                ary.append(nda)
                size = len(nda)
                # import pdb; pdb.set_trace()
                print(f"{size}こ 受信しました")
                # print(str(sys.getsizeof(res.points[0])* size / 1024), " KB")
                recieve_time = datetime.now()
                send_time = datetime.strptime(res.timestamp, "%Y%m%d%H%M%S%f")
                print(f"overhead time", recieve_time - send_time)

                cnt += size
            elapsed_time = time.time() - start
            print(f"受信に {elapsed_time}秒かかりました")
            print(f"total recieve {cnt}")
        except grpc.RpcError as e:
            print(e.details())
            # break

    npcd = np.concatenate(ary)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(npcd)
    o3d.io.write_point_cloud('./pointcloud_client.ply', pcd, write_ascii=True)

    print("finish client")

# ============================================================
# Awake
# ============================================================


# ============================================================
# main
# ============================================================
if __name__ == '__main__':
    run()
