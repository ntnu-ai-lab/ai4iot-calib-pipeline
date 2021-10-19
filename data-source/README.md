Before any call to the data source service, the user must input credentials for some external APIs. The data source server expects a config file named `.aqdata` under the path `/config/.aqdata` with the credentials for the Span and MET APIs (https://span.lab5e.com and https://frost.met.no/index.html), with the format below.

      #IOT data
      iot_token=<user token>

      #MET API
      met_id=<user id>
