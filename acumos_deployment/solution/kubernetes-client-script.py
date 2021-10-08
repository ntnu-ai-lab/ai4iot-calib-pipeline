import os
import re
import glob
import yaml
import json
import socket
import subprocess
import argparse


class DockerInfo:
    def __init__(self):
        print("")

    def update_node_port(self, ports_mapping, filename):
        print("Start updating the docker info Json : ")
        with open(filename, "r") as jsonFile:
            data = json.load(jsonFile)

        for x in range(len(data["docker_info_list"])):
            container_name = (data["docker_info_list"][x]["container_name"]).lower()
            data["docker_info_list"][x]["port"] = ports_mapping[container_name]

            ###  Updates the container names
            data["docker_info_list"][x]["container_name"] = container_name

            ### Update the ip_address
            ip_address = (data["docker_info_list"][x]["ip_address"]).lower()
            data["docker_info_list"][x]["ip_address"] = ip_address

        print("update_node_port: %s" % data["docker_info_list"])

        with open(filename, "w") as jsonFile:
            json.dump(data, jsonFile)

        print("\n Docker info file is successfully updated  ")


class Deployment:
    def __init__(self, start_port=30000, end_port=32767, path_dir=""):
        self.path_dir = path_dir
        self.start_port = start_port
        self.end_port = end_port
        self.port_mapping = dict()
        self.free_ports = None

    def determine_free_ports(self):
        # ask which ports are used
        process = subprocess.run([
            'kubectl', 'get', 'svc', '--all-namespaces', '-o',
            'go-template={{range .items}}{{range.spec.ports}}{{if .nodePort}}{{.nodePort}}{{"\\n"}}{{end}}{{end}}{{end}}'],
            check=True, stdout=subprocess.PIPE, universal_newlines=True)

        # get the used ports into a set
        used_ports = set([
            int(x.strip()) for x in process.stdout.split('\n') if x.strip() != ''
        ])
        # print("determine_free_ports: used_ports=%s" % used_ports)

        # create the list of free ports
        self.free_ports = [
            p
            for p in range(self.start_port, self.end_port + 1)
            if p not in used_ports
        ]
        # print("determine_free_ports: free_ports=%s" % self.free_ports)

    def get_next_free_port(self) -> int:
        if self.free_ports is None:
            self.determine_free_ports()
        if len(self.free_ports) > 0:
            return self.free_ports.pop(0)
        else:
            raise RuntimeError("There is no available free port in your max_port range")

    def get_current_dir(self):
        return os.getcwd()

    def is_service(self, file_name):
        with open(file_name) as f:
            doc = yaml.safe_load(f)
        ret = None
        if doc['kind'] == "Service":
            ret = True
        else:
            ret = False
        # print("is_service(", file_name, "returning", ret)
        return ret

    def set_image_pull_policy(self, deployment_file_name, new_policy='Always'):
        '''
        Permits to update a deployment YAML file so that the image will always be re-downloaded by kubernetes
        This is very useful for development/debugging but should not be used in production
        '''
        with open(deployment_file_name) as f:
            doc = yaml.safe_load(f)

        try:
            for c in doc['spec']['template']['spec']['containers']:
                old_policy = c.get('imagePullPolicy', None)
                if old_policy is not None and old_policy != new_policy:
                    print("set_image_pull_policy changing imagePullPolicy from", old_policy, "to", new_policy)
                elif old_policy is None:
                    print("set_image_pull_policy setting imagePullPolicy to", new_policy)
                c['imagePullPolicy'] = new_policy

            with open(deployment_file_name, "w") as f:
                yaml.dump(doc, f)
        except Exception:
            # if we process a file that is not a deployment - warn
            print("WARNING: set_image_pull_policy encountered incompatible input file", deployment_file_name)

    def set_node_port(self, file_name, node_port):
        print("set_node_port in", file_name, "to", node_port)
        with open(file_name) as f:
            doc = yaml.safe_load(f)

        # Tags are hardcoded according to template of kubernetes client

        doc['spec']['ports'][0]['nodePort'] = node_port
        ### port is also same as node_port
        doc['spec']['ports'][0]['port'] = node_port

        name = doc['metadata']['name']

        self.port_mapping[name] = node_port

        with open(file_name, "w") as f:
            yaml.dump(doc, f)

    def apply_deployment_services(self, file_name, node_port, namespace):
        print("apply_deployment_services file_name=", file_name)
        if self.is_service(file_name):
            self.set_node_port(file_name, node_port)
        else:
            self.set_image_pull_policy(file_name, 'Always')

        process = subprocess.run(['kubectl', '-n', namespace, 'apply', '-f', file_name], check=True,
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        output = process.stdout
        name = output.split(" ")
        print("  apply got %s" % name)
        return name[0]

    def delete_deployment_services(self, names, namespace):
        for name in names:
            process = subprocess.run(['kubectl', '-n', namespace, 'delete', str(name)], check=True,
                                     stdout=subprocess.PIPE,
                                     universal_newlines=True)
        output = process.stdout
        print("delete_deployment_services output %s" % output)

    def web_ui_service(self, file_name, namespace, node_port):
        print("web_ui_service file_name =", file_name, "node_port =", node_port)
        port_name = "webui"
        target_port = 8062
        with open(file_name) as f:
            doc = yaml.safe_load(f)

        # Value is hardcoded according to template of kubernetes client
        if not "webui" in doc['metadata']['name']:
            print("  added webui suffix")
            name1 = (doc['metadata']['name']) + "webui"
            doc['metadata']['name'] = name1
            # doc['spec']['selector']['app'] = name1

        doc['spec']['ports'][0]['name'] = port_name
        doc['spec']['ports'][0]['nodePort'] = node_port
        doc['spec']['ports'][0]['port'] = node_port
        doc['spec']['ports'][0]['targetPort'] = target_port

        name = doc['metadata']['name']
        self.port_mapping[name] = node_port
        result = file_name.split('.')
        result[0] = result[0] + '_webui.'
        file_name_new = result[0] + result[1]

        if "_webui.yaml" in file_name:
            with open(file_name, "w") as f:
                yaml.dump(doc, f)
        else:
            with open(file_name_new, "w") as f:
                yaml.dump(doc, f)

        return self.apply_deployment_services(file_name_new, node_port, namespace)

    def get_namespaces(self):
        process = subprocess.run(['kubectl', 'get', 'namespaces'], check=True,
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        output = process.stdout
        print("get_namespaces: output %s type %s" % (output, type(output)))
        return output

    def get_service_ip_address(self, namespce, service_name):
        process = subprocess.run(['kubectl', '-n', namespce, 'get', service_name], check=True, stdout=subprocess.PIPE,
                                 universal_newlines=True)
        # print(process.type())
        output = process.stdout
        name = output.split(" ")
        name1 = [x for x in name if x]
        return name1[7]

    def get_node_ip_address(self, namespce):
        process = subprocess.run(['kubectl', '-n', namespce, 'get', 'node', '-o', 'wide'], check=True,
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        # print(process.type())
        output = process.stdout
        name = output.split(" ")
        name1 = [x for x in name if x]
        return name1[14]

    def is_valid_namespace(self, namespace, existing_namespace):

        result = [x for x in (re.split('[  \n]', existing_namespace)) if x]
        if result.__contains__(namespace):
            # print(result.__contains__(namespace))
            index = result.index(namespace)
            # print(index)
            if result[index + 1] == 'Active':
                print("Given namespace is active ")
                return True
            else:
                print("Given namespace is inactive ")
                return False
        else:
            print("Name of your given namespace is invalid")
            return False

    def is_orchestrator_present(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return True


def main():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('--namespace', '-n', action='store', type=str, required=True,
                           help='name of namespace is required ')
    # Execute parse_args()
    args = my_parser.parse_args()
    # print(args.namespace)

    namespace = args.namespace
    path_dir = os.getcwd()
    deployment_dir = path_dir + "/deployments"
    deployment = Deployment(path_dir=deployment_dir)
    output = deployment.get_namespaces()

    if deployment.is_valid_namespace(namespace, output):
        if os.path.isdir(deployment.path_dir):
            files = glob.glob(deployment.path_dir + "/*.yaml")
            node_port = 0
            names = []  ## this is used for deletion.
            for file in files:
                if file.endswith('webui.yaml'):
                    continue
                if deployment.is_service(file):
                    node_port = deployment.get_next_free_port()
                    node_port_web_ui = deployment.get_next_free_port()
                    names.append(deployment.web_ui_service(file, namespace, node_port_web_ui))
                names.append(deployment.apply_deployment_services(file, node_port, namespace))
            # deployment.delete_deployment_services(names)
            print(deployment.port_mapping)

            dockerInfo = DockerInfo()
            dockerfilename = path_dir + "/dockerinfo.json"
            if os.path.exists(dockerfilename):
                dockerInfo.update_node_port(deployment.port_mapping, dockerfilename)
        else:
            print("Path to the target directory is invalid :  ")

        if deployment.is_orchestrator_present("orchestrator_client.py", path_dir):
            print("Node IP-address : " + deployment.get_node_ip_address(namespace))
            print("Orchestrator Port is : " + str(deployment.port_mapping.get('orchestrator')))
        else:
            print("Thank you")
    else:
        print("Existing namespaces are")
        print(output)


if __name__ == '__main__':
    main()