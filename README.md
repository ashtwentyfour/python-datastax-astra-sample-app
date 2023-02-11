# Python Flask Microservice Integration with DataStax Astra

The Python [Flask](https://flask.palletsprojects.com/en/2.2.x/) application in this repository uses [DataStax Astra](https://www.datastax.com/products/datastax-astra) Cassandra for persistent storage. The service can be used to store (and retrieve) fitness tracker data (time series data pertaining to physical activity, sleep and weight loss/gain)

The application is an example of how a simple microservice can be configured to integrate with DataStax and hosted on a [GCP GKE]() cluster by using [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) to access DataStax credentials from [Secret Manager](https://cloud.google.com/secret-manager)

## Installation

### Prerequisites

* Create a DataStax account and a new [Keyspace](https://docs.datastax.com/en/astra-classic/docs/manage/about-keyspaces.html)
* Download the 'secure_connect_bundle' and save the DataStax API credentials (client ID and client secret) as described [here](https://docs.datastax.com/en/astra-classic/docs/connect/drivers/connect-python.html). The bundle and the credentials can be downloaded/saved by logging into the DataStax web portal
* Access to a [Google Cloud (GCP)](https://cloud.google.com/) account

### Deployment

* Upload the DataStax 'secure_connect_bundle' ZIP to the Secret Manager by creating a new application secret called 'datastax_connect_bundle_1'
* Create two more secrets where the secret values are the DataStax client ID and client secret respectively ('datastax_client_id' and 'datastax_client_secret')
* Create a new GKE cluster and connect to the cluster by udating the [kubeconfig](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/):

```
$ gcloud container clusters get-credentials test-cluster-01 --region us-east1 --project test-gcp-project-01
```

* Create a new namespace and service account:

```
$ kubectl create ns gcp-python-cassandra
$ kubectl create serviceaccount python-cassandra-sa --namespace=gcp-python-cassandra
```

* Enable Worload Identity on the cluster:

```
$ gcloud container clusters update test-cluster-01 --workload-pool=pluralsight-gcp-infrastructure.svc.id.goog --zone us-east1-b
```

* Install the [Secrets Store CSI Driver](https://secrets-store-csi-driver.sigs.k8s.io/getting-started/installation.html) which allows workloads to access secrets from Secret Manager as files mounted in Kubernetes Pods
* Git clone the following [repository](https://github.com/GoogleCloudPlatform/secrets-store-csi-driver-provider-gcp.git) and execute (to install the Google plugin DaemonSet & additional RoleBindings)

```
$ kubectl apply -f deploy/provider-gcp-plugin.yaml
```

* Create a new GCP [Service Account](https://cloud.google.com/iam/docs/service-accounts)

```
$ gcloud iam service-accounts create k8s-secret-reader-02 --display-name="Read k8s secrets"
```

* Grant the IAM service account read-only permissions to the secrets:

```
$ gcloud secrets add-iam-policy-binding datastax_connect_bundle_1 --member=serviceAccount:k8s-secret-reader-02@test-gcp-project-01.iam.gserviceaccount.com --role='roles/secretmanager.secretAccessor'

$ gcloud secrets add-iam-policy-binding datastax_client_id --member=serviceAccount:k8s-secret-reader-02@test-gcp-project-01.iam.gserviceaccount.com --role='roles/secretmanager.secretAccessor'

$ gcloud secrets add-iam-policy-binding datastax_client_secret --member=serviceAccount:k8s-secret-reader-02@test-gcp-project-01.iam.gserviceaccount.com --role='roles/secretmanager.secretAccessor'
```

* Bind the IAM service account to the GKE service account:

```
$ gcloud iam service-accounts add-iam-policy-binding k8s-secret-reader-02@test-gcp-project-01.iam.gserviceaccount.com --member=serviceAccount:test-gcp-project-01.svc.id.goog[gcp-python-cassandra/python-cassandra-sa] --role='roles/iam.workloadIdentityUser'
```

* Annotate the GKE service account:

```
$ kubectl annotate serviceaccount python-cassandra-sa --namespace=gcp-python-cassandra iam.gke.io/gcp-service-account=k8s-secret-reader-02@test-gcp-project-01.iam.gserviceaccount.com
```

* Create the [SecretProviderClass](https://github.com/GoogleCloudPlatform/secrets-store-csi-driver-provider-gcp#usage):

```
$ kubectl apply -f deployment/manifests/secret.yml
```

* Deploy the application using:

```
$ kubectl apply -f deployment/manifests/deployment.yml
```

* Validate that the Pod is running and check the log messages for successful health check messages: 

```
$ kubectl logs python-cassandra-b45984ff7-g8247 -n gcp-python-cassandra

Defaulted container "python-cassandra-container" out of: python-cassandra-container, copy-secret-bundle (init)
2023-02-11 05:46:02,369 - DEBUG - Table 'health_tracker_data_keyspace_1.activity' already exists
2023-02-11 05:46:02,376 - DEBUG - Table 'health_tracker_data_keyspace_1.sleep' already exists
2023-02-11 05:46:02,383 - DEBUG - Table 'health_tracker_data_keyspace_1.weightloss' already exists
 * Serving Flask app 'app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://10.8.2.10:8080
Press CTRL+C to quit
10.8.2.1 - - [11/Feb/2023 05:46:19] "GET /health/ready HTTP/1.1" 200 -
10.8.2.1 - - [11/Feb/2023 05:46:29] "GET /health/ready HTTP/1.1" 200 -
```

* The application can be exposed as a service of type 'LoadBalancer' for test purposes:

```
$ kubectl apply -f service.yml
$ kubectl get svc -n gcp-python-cassandra
```

### Testing

* Add physical activity test data for a user with ID = 'd6e8a4a2-a8a7-11ed-afa1-0242ac120002' by running:

```
$ curl -X PUT $SERVICE_IP:8080/add/activity -H "Content-Type: application/json" -d '{"id": "d6e8a4a2-a8a7-11ed-afa1-0242ac120002", "date": "2022-10-01", "totalsteps": 12100, "calories": 1801, "totaldistance": 8.5, "sedentaryminutes": 650, "veryactiveminutes": 27, "fairlyactiveminutes": 20, "lightlyactiveminutes": 200}'
```

* Add sleep data:

```
$ curl -X PUT $SERVICE_IP:8080/add/sleep -H "Content-Type: application/json" -d '{"id": "d6e8a4a2-a8a7-11ed-afa1-0242ac120002", "date": "2022-10-01", "sleeptime": "2022-10-01 01:30:00", "sleepminutes": 400, "bedminutes": 430, "sleeprecords": 1}'
```

* Add weight and BMI data:

```
$ curl -X PUT $SERVICE_IP:8080/add/weight -H "Content-Type: application/json" -d '{"id": "d6e8a4a2-a8a7-11ed-afa1-0242ac120002", "date": "2022-10-01", "weightkgs": 52.445630003952, "fat": 22, "BMI": 22.54778900021}'
```

* Retrieve activity data for user 'd6e8a4a2-a8a7-11ed-afa1-0242ac120002':

```
$ curl $SERVICE_IP:8080/d6e8a4a2-a8a7-11ed-afa1-0242ac120002/activity

{"days":[{"calories":1801,"date":"2022-10-01","fairlyactiveminutes":20,"lightlyactiveminutes":200,"sedentaryminutes":650,"totaldistance":8.5,"totalsteps":12100,"veryactiveminutes":27}],"id":"d6e8a4a2-a8a7-11ed-afa1-0242ac120002"}
```

* Endpoints ```/{user_id}/sleep``` and ```/{user_id}/weightloss``` can be called to fetch sleep and weight data respectively