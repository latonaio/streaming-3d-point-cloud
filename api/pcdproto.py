"""NumPy ndarray to protobuf serialization and deserialization"""
from io import BytesIO

import numpy as np

from .PointCloud_pb2 import PointReply


def ndarray_to_proto(npcd: np.ndarray, timestamp: str) -> PointReply:
    npcd_bytes = BytesIO()
    np.save(npcd_bytes, npcd, allow_pickle=False)

    return PointReply(ndarray_pcd=[npcd_bytes.getvalue()], timestamp=timestamp)


def proto_to_ndarray(nda_proto: PointReply) -> np.ndarray:

    npcd_bytes = BytesIO(nda_proto.ndarray_pcd[0])

    return np.load(npcd_bytes, allow_pickle=False)
