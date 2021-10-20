### Prerequisites

- Install Docker: https://docs.docker.com/get-docker/

### Data Source

**1)** Go to folder and build the docker container.

`cd data-source && ./docker-build.sh`

**2)** Launch the container with the service

`./docker-run.sh`
      
Copy the config file to the data source container with the command `docker cp <orig_file> data-source:/config/.aqdata`  
Check the README inside [data source](data-source.md) for details on the config file.

### Calibration

**1)** Go to folder and build the docker container.

`cd calibration && ./docker-build.sh`

**2)** Launch the container with the service

`./docker-run.sh`

### Visualization

**1)** Go to folder and build the docker container.

`cd visualization && ./docker-build.sh`

**2)** Launch the container with the service

`./docker-run.sh`

### Orchestration

Orchestrator is the term to the script which connects to all running modules and passes messages forward through the pipeline.

**1)** Before running the orchestrator, it is needed to copy the protobuf message definitions to its folder and compile locally (the client needs to be aware of the message types)

`cd local-orchestrator && ./build_protobuf.sh`

**2)** Run the orchestration script

`./run-orchestrator.sh`

The output of the pipeline is available through the webui available at the address `localhost:8000`
