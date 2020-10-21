from grpc.tools import protoc

protoc.main(
    (
        '',
        '-I.',
        '--python_out=../api',
        '--grpc_python_out=../api',
        './PointCloud.proto'
    )
)
