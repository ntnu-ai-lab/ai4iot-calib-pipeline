### Download solution from Acumos

Go to the visual studio of the AI4EU Experiments and open the *ai4iot-calib* solution. Then click on Deploy -> Deploy to Local.

![image](https://user-images.githubusercontent.com/45718165/137911279-88d2fb1f-442a-4d25-8cbf-4b01c3ee3084.png)

And download the solution.zip exported by the pltaform.

![image](https://user-images.githubusercontent.com/45718165/137911369-dcd0ab85-5362-403d-9bb4-89c2e984333c.png)

Save the file , extract it locally, and `cd solution`. From now on, we assume the user is working within the solution folder.

### Set up kubernetes and containers

**1)** Start minikube

`minikube start`

**2)** Create a new namespace

`kubectl create namespace <namespace_id>`

Ex.: `kubectl create namespace ai4iot`

**3)** Run deployment script

`python kubernetes-client-script.py -n <namespace_id>`

Ex.: `python kubernetes-client-script.py -n ai4iot`

Note the info printed by this script, as in the example below, the command for the orchestrator client will be used in a further step.

![image](https://user-images.githubusercontent.com/45718165/137909352-7e6377a3-0831-47b8-8206-51885a30b54a.png)

**4)** Run `watch kubectl get all -n <namespace_id> -o wide` (Ex.: `watch kubectl get all -n ai4iot -o wide`) and wait until all pods are with STATUS Running, as in the following example. After that, CTRL+C to stop the watch. This is needed to ensure that all containers are up and running before running the pipeline.

![image](https://user-images.githubusercontent.com/45718165/137887263-854da8d7-0acc-441f-9196-2f3110bee814.png)

**5)** Before running the pipeline, the user must copy into the data source container his/hers credentials to access external data. Check data-source README for more info on this configuration. This is done through the `kubectl cp` command. A script with the preconfigured command is available under the *utils* folder, which can be ran as follows:  
`utils/copy_file_to_container.sh <orig_file> <namespace_id>`

Ex.: `utils/copy_config_kubernetes.sh ~/.aqdata ai4iot`

The full command is:

`kubectl cp <orig_file> <namespace_id>/$(kubectl get pod -l app=data-source1 -o jsonpath="{.items[0].metadata.name}" -n <namespace_id>):/config/.aqdata`

It is expected that the AI4EU Experiments offers this functionality in future versions. For now we have to do it manually.

### Run the pipeline
**1)** Run the orchestrator client

Run a single time. 
`python orchestrator_client/orchestrator_client.py --endpoint=<node_ip>:<orchestrator_port> --basepath=./`

Ex.: `python orchestrator_client/orchestrator_client.py --endpoint=192.168.49.2:30004 --basepath=./`

Run with a given frequency, where <n_seconds> is the number of seconds between each call.   
`watch -n <n_seconds> python orchestrator_client/orchestrator_client.py --endpoint=<node_ip>:<orchestrator_port> --basepath=./`

Ex. for every hour: `watch -n 3600 python orchestrator_client/orchestrator_client.py --endpoint=192.168.49.2:30004 --basepath=./`

**2)** Visualize the output

The visualization module prints output in the format of an html page available through a webui port in the kubernetes cluster.  
To find the webui port run the command `kubectl get services -n <namespace_id>` and search for the port of the visualization1webui, as in the following example:  

![image](https://user-images.githubusercontent.com/45718165/137888386-2423a4ba-901a-4a42-9c30-3a1ce4ee5a7e.png)

The ip address is the same used for calling the orchestrator, or the command `minikube ip` can be used to find it.

Finally, open the respective address in any browser: `<node_ip>:<visualization_webui_port>`