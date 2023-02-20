# API Gateway Lambda Proxy Integration Boilerplate
This boilerplate provides a quick start for an API Gateway Lambda Proxy Integration. It includes the following features:
- Public REST API Gateway 
- single resource and a proxy method for any HTTP method
- Lambda function with a handler that returns a 200 response and the html returned by google.com
# Instructions
- Clone this repository
- update lambda_function.py with your code
- update installed packages in packages folder using ```pip install --target ./packages {package name}```
- zip the contents of the packages folder into the root folder:
    - ```cd packages```
    - ```zip -r ../packages.zip .```
- zip the contents of the root folder:
    - ```cd ..```
    - ```zip lambda.zip lambda_function.py```
    - note: if you have additional files in the root folder, you can add them to the zip file using ```zip lambda.zip {file name}```
- package the cloudformation template (e.g. upload lambda.zip to S3 and output the updated template with s3 absolute references)
    - ```aws cloudformation package --template-file template.yaml --s3-bucket {bucket name} --output-template-file packaged-template.yaml```
- deploy the cloudformation template (hint: you will need capabilitiy to create IAM roles)
    - ```aws cloudformation deploy --template-file packaged-template.yaml --stack-name {stack name} --capabilities CAPABILITY_NAMED_IAM```
- describe the stack to get the API Gateway endpoint
    - ```aws cloudformation describe-stacks --stack-name {stack name}```
    - note: the endpoint is in the Outputs section
- test the endpoint
    - ```curl {endpoint}```
    - can also reach in browser by navigating to the endpoint
    - note: you should see the html returned by google.com