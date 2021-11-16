### Prerequisites

- Install Docker: https://docs.docker.com/get-docker/

### Container set up

**1)** Pull containers from Docker Hub

`docker pull tsveiga/ai4iot:datasource`  
`docker pull tsveiga/ai4iot:calibration`  
`docker pull tsveiga/ai4iot:visualization`

**2)** In different terminals, run:

`docker run -p 8060:8061 --name data-source --rm -it tsveiga/ai4iot:datasource`  
`docker run -p 8061:8061 --name calibration --rm -it tsveiga/ai4iot:calibration`  
`docker run -p 8000:8062 -p 8062:8061 --name visualization --rm -it tsveiga/ai4iot:visualization`
      
**3)** Copy the config file to the data source container, check the README inside [data source](data-source.md) for details on the config file.
 
 `docker cp <orig_file> data-source:/config/.aqdata`  

### Orchestration

Orchestrator is the term to the script which connects to all running modules and passes messages forward through the pipeline.

**1)** Before running the orchestrator, it is needed to copy the protobuf message definitions to its folder and compile locally (the client needs to be aware of the message types)

`cd local-orchestrator && ./build_protobuf.sh`

**2)** Run the orchestration script

`./run-orchestrator.sh`

The output of the pipeline is available through the webui available at the address `localhost:8000`. Open it in any browser and you'll find a siple webpage presenting the output of the pipeline for the available sensors. Currently, only `Elgeseter` and `Torget`. Navigate through the buttons on the webpage to visualize either of them. The output includes plots for PM2.5 and PM10 measurements for the past 12 hours, both before and after the calibration procedure.

![image](https://user-images.githubusercontent.com/45718165/138251559-a64c8738-4ee0-4b78-a6d2-fede18e0ec0f.png)
