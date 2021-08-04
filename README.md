## AWS Docker Templates - Express

The AWS Docker Templates for Flask from TinyStacks enable launching a [Flask]() application as a Docker container using an AWS CodePipeline pipeline. The template includes its own small Flask sample application, enabling developers to start a new Flask project immediately. Developers can also take the AWS CodePipeline-specific files in this template and use them to ship an existing Flask application as a Docker image on AWS. 

## License

This sample code is made available under a modified MIT license. See the LICENSE file.

## Outline

- [Prerequisites](#prerequisites)
- [Overview](#overview)
  - [Sample Application](#sample-application)
  - [Dockerfile](#dockerfile)
  - [Build Template](#build-template)
  - [Release Template](#release-template)
- [Getting Started](#getting-started)
  - [Existing Project](#existing-project)
- [Known Limitations](#known-limitations)

## Prerequisites

If you wish to build and test the Flask server (both as a standalone server and hosted inside of a Docker container) before publishing on AWS, you should have [Python](https://www.python.org/downloads/), [Flask](https://flask.palletsprojects.com/en/2.0.x/), and [Docker](https://docs.docker.com/get-docker/) installed locally. 

This solution makes use of a Docker image that comes with a Flask environment pre-installed. If you wish to run just the Docker container locally, you will only need Docker.

This document also assumes that you have access to an AWS account. If you do not have one, [create one before getting started](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/).

If executed locally, the use of AWS DynamoDB and Amazon Cognito in the Flask application will require that you have valid credentials for AWS saved on your local computer. We recommend configuring your credentials locally as a login profile and using the `AWS_PROFILE` environment variable to designate which set of credentials to use. For other options on setting AWS credentials, see [Setting Credentials in Node.js](https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/setting-credentials-node.html).

Further prerequisites for running these templates on AWS are provided below.

## Overview

Flask is a lightweight Python-based framework for developing REST APIs. The hallmark of the Flask framework is that it is minimal and unopinionated; it provides a basic framework for API definition and routing and leaves other major decisions, such as data storage, entirely up to the user. 

This sample contains the following files: 

* A sample Flask API, defined in the app.py file. 
* A Dockerfile that builds the Flask file as a Docker image. 
* A requirements.txt file that defines the libraries your Flask application will require when installed inside of Docker. 
* A wsgi.py file for running your Flask application under the gunicorn server on your Docker image.
* A `build.yml` file for AWS CodeBuild that builds the image and pushes it to Amazon Elastic Container Registry (ECR). 
* A `release.yml` file for AWS CodeBuild that deploys the image stored in ECR to a Amazon Elastic Container Service (ECS) cluster. 

Users can use the `build.yml` and `release.yml` YAML files to create an AWS CodePipeline pipeline that compiles the latest application into a Docker image, which is then stored in an Amazon Elastic Container Registry (ECR) registry that is accessible to the user. The Flask application itself is deployed onto AWS as a Docker container using Amazon Elastic Container Service (Amazon ECS) onto one of the user's available ECS clusters. 

### Sample Application

The sample application is a simple CRUD (Create/Read/Update/Delete) application that can store data either in memory or in an AWS DynamoDB database table. When this application runs, it presents a set of REST API endpoints that other applications can call to store data. 

The file `app.py` defines the REST API endpoints for the application. There are three sets of endpoints defined, each with slightly different functionality. 

| Endpoint Type  | Description |
| ------------- | ------------- |
| `/item`  | Stores the Item in memory. |
| `/db-item`  | Stores the item in an AWS DynamoDB table.  |
| `/authenticated-item`  | Like `/db-item`, but requires that the API user be logged in with an Amazon Cognity Identity. All records saved with this API are saved with the user's Cognito ID. When performing read and update operations with this API, users can only access the records that they created. |

The server uses the same endpoint for all CRUD operations, distinguishing between them with HTTP verbs: 

| Endpoint Type  | Description |
| ------------- | ------------- |
| PUT  | Create  |
| GET | Read  |
| POST  | Update  |
| DELETE  | Delete  |

#### Running the Flask Server Directly

To test out the sample application directly before you package it into a Dockerfile, clone this project locally, then create a virtual environment.

```
python -m venv venv
```

Next, activate your virtual environment and run the Flask application. (Note: You only need to define the variables AWS_PROFILE and TABLE_NAME if you plan to test the endpoints that store data in a DynamoDB table. Otherwise, these can be omitted.)

On Linux:

```
. venv/bin/activate

pip install -r requirements.txt

AWS_PROFILE=[profile name] 
TABLE_NAME=[table name] 

flask run -p 8000 --host 0.0.0.0
```

On Windows (Powershell):

```
venv\Scripts\activate

pip install -r requirements.txt

$env:AWS_PROFILE=[profile name] 
$env:TABLE_NAME=[table name] 

flask run -p 8000 --host 0.0.0.0
```

To test that the server is running, test its `/ping` endpoint from a separate command line window: 

```
curl http://127.0.0.1/ping
```

If the server is running, this call will return an HTTP 200 (OK) result code. 

#### Adding an Item in Memory

To add an item in memory, call the `/item` endpoint with an HTTP PUT verb. This can be done on Unix/MacOS systems using cUrl: 

```
curl -H "Content-Type: application/json" -X PUT -d '{"title":"my title", "content" : "my content"}' "http://127.0.0.1/item"
```

On Windows Powershell, use Invoke-WebRequest: 

```powershell
$item = @{
    title="my title"
    content="my content"
}
$json = $item |convertto-json
$response = Invoke-WebRequest 'http://127.0.0.1/item' -Method Put -Body $json -ContentType 'application/json'
```

The return result will be the same item but with a UUID that serves as its index key into the in-memory dictionary where the entry is stored. 

#### Adding an Item to a DynamoDB Table

The sample application can store items as full JSON files in a DynamoDB table. The name of the table used is retrieved from the environment variable `TABLE_NAME`. 

To write to DynamoDB, the application must be running in a context in which it has been granted permissions to access the DynamoDB table.

### Dockerfile

The Dockerfile copies the sample application into a Docker image and runs a Flask server. 

A Dockerfile uses a Docker base image stored in a public Docker repoistory and then adds functionality to the image required by your application. This project's Dockerfile is based on the 
