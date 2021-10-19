# Input arguments
# 1 - path to local config file (ex.: ~/.aqdata)
# 2 - kubernetes namespace (ex.: ai4iot)

kubectl cp $1 $2/$(kubectl get pod -l app=data-source1 -o jsonpath="{.items[0].metadata.name}" -n $2):/config/.aqdata
