### Prerequisites

- Install Docker: https://docs.docker.com/get-docker/

- Install needed python packages: `pip3 install -r requirements.txt`

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

This script uses the [schedule](https://schedule.readthedocs.io/en/stable/) package to schdule regular calls to the pipeline. The line of interest for this is the one with the following:

`schedule.every().hour.at(":15").do(update_data)`

Different combinations are allowed by the scheduler. For instance, to run every 10 seconds one should add the line `schedule.every(10).seconds.do(update_data)`. Follow the package documentation to implement your own scheduling. Note, however, that the visualization module is implemented such that it prints only one data point per hour.

The output of the pipeline is available through the webui available at the address `localhost:8000`. Open it in any browser and you'll find a simple webpage presenting the output of the pipeline for the available sensors. Currently, only `Elgeseter` and `Torget`. Navigate through the buttons on the webpage to visualize either of them. The output includes plots for PM2.5 and PM10 measurements for the past 12 hours, both before and after the calibration procedure.

![image](https://user-images.githubusercontent.com/45718165/143457667-9fba09d4-b0b3-494f-ab63-4378e5d91c63.png)

