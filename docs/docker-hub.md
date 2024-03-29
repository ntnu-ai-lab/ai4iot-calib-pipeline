### Prerequisites

- Install Docker: https://docs.docker.com/get-docker/

- Install the schedule python package: `pip3 install schedule`

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

This script uses the [schedule](https://schedule.readthedocs.io/en/stable/) package to schdule regular calls to the pipeline. The line of interest for this is the one with the following:

`schedule.every().hour.at(":15").do(update_data)`

Different combinations are allowed by the scheduler. For instance, to run every 10 seconds one should add the line `schedule.every(10).seconds.do(update_data)`. Follow the package documentation to implement your own scheduling. Note, however, that the visualization module is implemented such that it prints only one data point per hour.

The output of the pipeline is available through the webui available at the address `localhost:8000`. Open it in any browser and you'll find a siple webpage presenting the output of the pipeline for the available sensors. Currently, only `Elgeseter` and `Torget`. Navigate through the buttons on the webpage to visualize either of them. The output includes plots for PM2.5 and PM10 measurements for the past 12 hours, both before and after the calibration procedure.

![image](https://user-images.githubusercontent.com/45718165/143457667-9fba09d4-b0b3-494f-ab63-4378e5d91c63.png)
