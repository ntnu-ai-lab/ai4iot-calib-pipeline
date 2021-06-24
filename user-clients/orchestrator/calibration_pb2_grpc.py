# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import calibration_pb2 as calibration__pb2


class CalibrationStub(object):
    """Define the service
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.calibrate_sample = channel.unary_unary(
                '/aqcalibration.Calibration/calibrate_sample',
                request_serializer=calibration__pb2.DataSample.SerializeToString,
                response_deserializer=calibration__pb2.CalibResponse.FromString,
                )


class CalibrationServicer(object):
    """Define the service
    """

    def calibrate_sample(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CalibrationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'calibrate_sample': grpc.unary_unary_rpc_method_handler(
                    servicer.calibrate_sample,
                    request_deserializer=calibration__pb2.DataSample.FromString,
                    response_serializer=calibration__pb2.CalibResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'aqcalibration.Calibration', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Calibration(object):
    """Define the service
    """

    @staticmethod
    def calibrate_sample(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/aqcalibration.Calibration/calibrate_sample',
            calibration__pb2.DataSample.SerializeToString,
            calibration__pb2.CalibResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
