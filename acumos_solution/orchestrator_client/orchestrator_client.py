#!/usr/bin/env python3
# ===================================================================================
# Copyright (C) 2021 Fraunhofer Gesellschaft, Peter Schueller. All rights reserved.
# ===================================================================================
# This Acumos software file is distributed by Fraunhofer Gesellschaft
# under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============LICENSE_END========================================================

# generic parallel orchestrator client
# arguments:
# --ip/-i <ip> --port/-p <port> --endpoint/-e <ip>:<port>
# functionality:
# read proto files from zip archive
# initialize, attach observer, run infinitely

import os
import sys
import logging
import argparse
import subprocess
import traceback
import threading
import grpc
from orchestrator_pb2 import OrchestrationObservationConfiguration
from typing import List, Optional

# TODO make this configurable in an upcoming version
DEFAULT_QUEUE_SIZE = 0
DEFAULT_ITERATIONS = 0

SRCDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

try:
    import orchestrator_pb2
    import orchestrator_pb2_grpc
except:
    # recompile orchestrator client protobuf file if import fails
    logging.warning("exception importing orchestrator_pb2 and orchestrator_pb2_grpc - recompiling!")
    import_dir = os.path.join(SRCDIR, '..', 'protobuf')
    subprocess.check_call(
        "python -m grpc_tools.protoc --python_out=%s --grpc_python_out=%s --proto_path=%s %s" % (
            SRCDIR, SRCDIR, import_dir, os.path.join(import_dir, 'orchestrator.proto')
        ),
        stderr=sys.stderr, shell=True)
    import orchestrator_pb2
    import orchestrator_pb2_grpc
    logging.info("successfully imported orchestrator_pb2  and orchestrator_pb2_grpc after compiling!")


class SolutionConfiguration:
    blueprint_path: str
    dockerinfo_path: str
    protofiles_paths: List[str]

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def dict(self):
        return {
            attr: getattr(self, attr)
            for attr in ['blueprint_path', 'dockerinfo_path', 'protofiles_paths']
        }


class RunConfiguration(SolutionConfiguration):
    endpoint: str
    observer_componentfilter: Optional[str]
    observer_namefilter: Optional[str]
    message_display: bool

    def __init__(self, **kwargs):
        self.observer_componentfilter = None
        self.observer_namefilter = None
        super().__init__(**kwargs)


def readfile(path) -> str:
    with open(path, 'rt') as f:
        return f.read()


def load_solution_configuration(basepath: str) -> SolutionConfiguration:
    '''
    detect solution configuration in basepath and load
    '''
    try:

        dij = os.path.join(basepath, 'dockerinfo.json')
        if not os.path.exists(dij):
            raise RuntimeError("could not find file '%s'" % dij)

        bpj = os.path.join(basepath, 'blueprint.json')
        if not os.path.exists(bpj):
            raise RuntimeError("could not find file '%s'" % bpj)

        msd = os.path.join(basepath, 'microservice')
        if not os.path.exists(msd):
            raise RuntimeError("could not find directory '%s'" % msd)

        pfpaths = [
            os.path.join(msd, protofile)
            for protofile in os.listdir(msd)
            if protofile.endswith('.proto')
        ]

        sc = SolutionConfiguration(
            blueprint_path=bpj,
            dockerinfo_path=dij,
            protofiles_paths=pfpaths)
        logging.info("load_solution_configuration returning %s", sc)

        return sc

    except Exception:
        logging.error("load_solution_configuration: error %s", traceback.format_exc())
        raise RuntimeError("could not load solution configuration from path '%s': expect files blueprint.json, dockerinfo.json, microservice/*.proto" % basepath)


class OrchestrationObserver(threading.Thread):
    def __init__(self, endpoint: str, message_display: bool, server_configuration: OrchestrationObservationConfiguration):
        super().__init__(daemon=False)
        self.endpoint = endpoint
        self.message_display = message_display
        assert isinstance(server_configuration, OrchestrationObservationConfiguration)
        self.server_configuration = server_configuration

    def run(self):
        try:
            channel = grpc.insecure_channel(self.endpoint)
            stub = orchestrator_pb2_grpc.OrchestratorStub(channel)
            for event in stub.observe(self.server_configuration):

                # omit event.run because we do not use it yet
                if event.name == 'exception':

                    # display exceptions in a special way
                    print("%s produced exception in method %s with traceback\n%s" % (
                        event.component, event.detail['method'], event.detail['traceback']))

                else:

                    if self.message_display:
                        display_detail = event.detail
                    else:
                        display_detail = {
                            k: v
                            for k, v in event.detail.items()
                            if k not in 'message'
                        }

                    # generic display
                    detailstr = ''
                    if len(display_detail) > 0:
                        detailstr = ' with details ' + ' '.join(
                            [f"{k}={repr(v)}" for k, v in display_detail.items()]
                        )
                    print("%s produced event '%s'%s" % (event.component, event.name, detailstr))

                sys.stdout.flush()

        except KeyboardInterrupt:
            # CTRL+C or SIGTERM should just terminate, not write any exception info
            pass
        except Exception:
            logging.error("observer thread terminated with exception: %s", traceback.format_exc())


def observe(endpoint: str, message_display, server_configuration) -> threading.Thread:
    '''
    create observer thread and start
    '''
    oot = OrchestrationObserver(endpoint, message_display, server_configuration)
    oot.start()
    return oot


def observe_initialize_run(config: RunConfiguration):
    logging.info("connecting to orchestrator")
    channel = grpc.insecure_channel(config.endpoint)
    stub = orchestrator_pb2_grpc.OrchestratorStub(channel)

    logging.info("creating observer")
    server_configuration = OrchestrationObservationConfiguration(
        name_regex='.*' if config.observer_namefilter is None else config.observer_namefilter,
        component_regex='.*' if config.observer_componentfilter is None else config.observer_componentfilter
    )
    #oot = observe(config.endpoint, config.message_display, server_configuration)

    logging.info("calling initialize")
    stub.initialize(orchestrator_pb2.OrchestrationConfiguration(
        blueprint=readfile(config.blueprint_path),
        dockerinfo=readfile(config.dockerinfo_path),
        protofiles={
            os.path.basename(fname) : readfile(fname)
            for fname in config.protofiles_paths
        },
        queuesize=DEFAULT_QUEUE_SIZE,
        iterations=DEFAULT_ITERATIONS,
    ))

    logging.info("calling run")
    # empty label = default
    # TODO implement configurable labels
    stub.run(orchestrator_pb2.RunLabel())

    # wait for observer to terminate
    #oot.join()


def main():
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-H', '--host', type=str, required=False, metavar='HOST', action='store',
        dest='host', help='The host name or IP address of the orchestrator.')
    ap.add_argument(
        '-p', '--port', type=int, required=False, metavar='PORT', action='store',
        dest='port', help='The network port of the orchestrator.')
    ap.add_argument(
        '-e', '--endpoint', type=str, required=False, metavar='IP:PORT', action='store',
        dest='endpoint', help='The endpoint (combination of host and port) of the orchestrator.')
    ap.add_argument(
        '-b', '--basepath', type=str, required=False, metavar='BASEPATH', action='store',
        dest='basepath', help='The path where dockerinfo.json, blueprint.json, and pipelineprotos.zip can be found.')
    ap.add_argument(
        '--messages', action='store_true',
        dest='messages', help='Display all messages during orchestration (otherwise message contents are hidden).')
    ap.add_argument(
        '-n', '--filtername', type=str, required=False, metavar='REGEX', action='store',
        dest='filtername', help='Regular expression for filtering events according to event.name (server-side). Default = ".*" (display all).')
    ap.add_argument(
        '-c', '--filtercomponent', type=str, required=False, metavar='REGEX', action='store',
        dest='filtercomponent', help='Regular expression for filtering events according to event.component (server-side). Default = ".*" (display all).')
    args = ap.parse_args()

    endpoint = args.endpoint
    if endpoint is None and args.host is not None and args.port is not None:
        endpoint = '%s:%d' % (args.host, args.port)

    if endpoint is None:
        ap.print_help()
        return -1

    sconfig = load_solution_configuration(args.basepath)
    params = sconfig.dict()
    params.update({'endpoint': endpoint, 'message_display': args.messages, 'observer_namefilter': args.filtername, 'observer_componentfilter': args.filtercomponent})
    rconfig = RunConfiguration(**params)
    observe_initialize_run(rconfig)

if __name__ == '__main__':
    main()
