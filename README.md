# PopViz
A utilize project to capture and visualize Cloudfront edge locations, similar to what is seen on the [Amazon Cloudfront product page](https://aws.amazon.com/cloudfront/details/)

#### world.json
A 110 meter resolution geojson file of the world, excluding Antarctica (if AWS adds a PoP there, we can add it back in). To regenerate this file, or to use something different, look here: https://geojson-maps.ash.ms/

#### cloudfront.json
This is a sample data file that contains the Cloudfront locations present when this repo was created. 

#### popviz.html
The one and only web page. This page uses Leaflet to display both the information in the world.json file and the cloudfront.json file. Ajax is used to asynchronously load both data files on page load. 

#### popviz.yaml
Cloudformation template to build the AWS resources associated with this project. This template includes some components of [SAM](https://github.com/awslabs/serverless-application-model) for convenience. 

#### lambda/popviz.py
The source code for the Lambda function that scrapes locations, geolocates place names, and builds the cloudfron.json geojson file. Note this function uses the [Google Maps Geolocation API](https://developers.google.com/maps/documentation/geolocation/intro) to translate locations to coordinates. To use thie API, you must have a Google account and an API key. 

To build this yourself:  

### 1. Build the Lambda package 
This command zips up the Lambda function, uploads it to the specified S3 bucket and outputs another Cloudformation template that references that bucket directly. 
```
aws cloudformation package --template-file popviz.yaml --s3-bucket <S3 bucket to upload Lambda package> --output-template-file package.popviz.yaml
```

### 2. Create the AWS resources.
Build the AWS resources, including an S3 bucket to host a simple static website, a Lambda function to generate the data file, and the IAM role and policy with permissions to upload to the created S3 bucket. (If you don't have a region set via ```aws configure``` you'll need to provide one on the command line, like ```--region us-west-2```)
```
aws cloudformation deploy --template-file package.popviz.yaml --stack-name <Your Stack Name> --parameter-overrides PopVizBucketName=<S3 Bucket Name> GoogleAPIKey=<Your Google API Key> --capabilities CAPABILITY_IAM 
```

### 3. Copy the web page and data files to the S3 bucket.
```
aws s3 cp popviz.html s3://<S3 Bucket Name>/popviz.html --acl public-read
aws s3 cp world.json s3://<S3 Bucket Name>/world.json --acl public-read
aws s3 cp cloudfront.json s3://<S3 Bucket Name>/cloudfront.json --acl public-read
```
