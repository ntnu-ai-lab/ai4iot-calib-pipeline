### Container set up

**1)** Pull containers from Docker Hub

`docker pull tsveiga/ai4iot:datasource`  
`docker pull tsveiga/ai4iot:calibration`  
`docker pull tsveiga/ai4iot:visualization`

**2)** In different terminals, run:

`docker run -p 8060:8061 --name data-source --rm -it tsveiga/ai4iot:datasource`  
`docker run -p 8061:8061 --name calibration --rm -it tsveiga/ai4iot:calibration`  
`docker run -p 8000:8062 -p 8062:8061 --name visualization --rm -it tsveiga/ai4iot:visualization`
      
**3)** Copy the config file to the data source container, check the README inside data-source for details on the config file.
 
 `docker cp <orig_file> data-source:/config/.aqdata`  

### Orchestration

Orchestrator is the term to the script which connects to all running modules and passes messages forward through the pipeline.

**1)** Before running the orchestrator, it is needed to copy the protobuf message definitions to its folder and compile locally (the client needs to be aware of the message types)

`cd local-orchestrator && ./build_protobuf.sh`

**2)** Run the orchestration script

`./run-orchestrator.sh`

The output of the pipeline is available through the webui available at the address `localhost:8000`