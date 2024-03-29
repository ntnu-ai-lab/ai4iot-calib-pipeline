### Prerequisites

In this illustrative tutorial, we use minikube as the tool to set up a local Kubernetes environment, although one can use any other which better suits his/her needs.

- Install Docker: https://docs.docker.com/get-docker/
- Install minikube: https://minikube.sigs.k8s.io/docs/start/
- Install Kubernetes: https://kubernetes.io/docs/tasks/tools/

### Download solution from Acumos

**Note: This approach is not currently generalizable due to an update on the platform orchestrator that is not fully compatible with previous container specification from the developer team. Briefly, the orchestrator is not properly terminated once a container returns a gRPC status error code, as defined in the [platform documentation](https://github.com/ai4eu/tutorials/blob/master/Container_Specification/ai4eu_container_specification.pdf). The issue has been reported and will be fixed.**

**As a workaround, a version of the solution with a manual fix is available in this repository under the folder `acumos_solution`. Follow the following section** ***Use pre-downloaded solution from Acumos*** **to set it up.**

~~Go to the Design Studio of the [AI4EU Experiments](https://aiexp.ai4europe.eu/#/home) and open the [*AI4IoT-Calibration*](https://aiexp.ai4europe.eu/#/marketSolutions?solutionId=0fbc7cc0-843a-489b-bab1-40e4d2700680&revisionId=478028bb-1c58-4641-9bc0-eba716119aec) solution. It is found on the Solution tab on the left side (figure below). Make sure to use the newest version of the solution.~~

~~![image](https://user-images.githubusercontent.com/45718165/144255264-a7d82db2-0c7c-4d6c-b07d-2f2212b72ca5.png)~~

~~Then click on Deploy -> Deploy to Local.~~

~~![image](https://user-images.githubusercontent.com/45718165/137911279-88d2fb1f-442a-4d25-8cbf-4b01c3ee3084.png)~~

~~And download the solution.zip exported by the platform.~~

~~![image](https://user-images.githubusercontent.com/45718165/137911369-dcd0ab85-5362-403d-9bb4-89c2e984333c.png)~~

~~Save the file , extract it locally, and move into the extracted folder with `cd solution`. From now on, we assume the user is working within the solution folder.~~

~~Install the package requirements for the orchestration:~~

~~`pip3 install -r requirements.txt`~~

### Use pre-downloaded solution from Acumos

In a terminal, move into the `acumos_solution` folder and install the needed requirements for orchestration:

`pip3 install -r requirements.txt`

### Set up kubernetes and containers

In a terminal, use the following commands to set up the kubernetes cluster and run the containers in the pipeline.

**1)** Start minikube

`minikube start`

**2)** Create a new namespace

`kubectl create namespace <namespace_id>`

Ex.: `kubectl create namespace ai4iot`

**3)** Run deployment script

`python3 kubernetes-client-script.py -n <namespace_id>`

Ex.: `python3 kubernetes-client-script.py -n ai4iot`

Note the info printed by this script, as in the example below, the command for the orchestrator client will be used in a further step.

![image](https://user-images.githubusercontent.com/45718165/137909352-7e6377a3-0831-47b8-8206-51885a30b54a.png)

**4)** Run `watch kubectl get all -n <namespace_id> -o wide` (Ex.: `watch kubectl get all -n ai4iot -o wide`) and wait until all pods are with STATUS Running, as in the following example. After that, CTRL+C to stop the watch. This is needed to ensure that all containers are up and running before running the pipeline.

![image](https://user-images.githubusercontent.com/45718165/137887263-854da8d7-0acc-441f-9196-2f3110bee814.png)

**5)** Before running the pipeline, the user must copy into the data source container his/hers credentials to access external data. Check the [data source](data-source.md) README for more info on this configuration. This is done through the `kubectl cp` command. A script with the preconfigured command is available under the *utils* folder, which can be ran as follows:  
`utils/copy_file_to_container.sh <orig_file> <namespace_id>`

Ex.: `utils/copy_config_kubernetes.sh ~/.aqdata ai4iot`

The full command is:

`kubectl cp <orig_file> <namespace_id>/$(kubectl get pod -l app=data-source1 -o jsonpath="{.items[0].metadata.name}" -n <namespace_id>):/config/.aqdata`

It is expected that the AI4EU Experiments offers this functionality in future versions. For now we have to do it manually.

### Run the pipeline
**1)** Run the orchestrator client

Here, we make use of the command outputed by the `kubernetes-client-script`. We present two options, first if one wants to run the pipeline only a single time:  
`python orchestrator_client/orchestrator_client.py --endpoint=<node_ip>:<orchestrator_port> --basepath=./`

Ex.: `python3 orchestrator_client/orchestrator_client.py --endpoint=192.168.49.2:30004 --basepath=./`

However, in our particular case, we need the calibration output to be updated every hour, since all the input data is also updated with that frequency. For that we can implement a chronjob. For now and for illustraton purposes, the most simple is to run the orchestrator client with a fixed frequency. For that we use the command `watch`, where <n_seconds> is the number of seconds between each call:  
`watch -n <n_seconds> python orchestrator_client/orchestrator_client.py --endpoint=<node_ip>:<orchestrator_port> --basepath=./`

Ex. for every hour: `watch -n 3600 python3 orchestrator_client/orchestrator_client.py --endpoint=192.168.49.2:30004 --basepath=./`

**2)** Visualize the output

The visualization module prints output in the format of an html page available through a webui port in the kubernetes cluster.  
The address where the visualization is published is available with the command:

`minikube -n <namespace_id> service --url visualization1webui`

Finally, open the respective address in any browser and you'll find a siple webpage presenting the output of the pipeline for the available sensors. Currently, only `Elgeseter` and `Torget`. Navigate through the buttons on the webpage to visualize either of them. The output includes plots for PM2.5 and PM10 measurements for the past 12 hours, both before and after the calibration procedure.

![image](https://user-images.githubusercontent.com/45718165/143457667-9fba09d4-b0b3-494f-ab63-4378e5d91c63.png)

