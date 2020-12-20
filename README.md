# s3-json-to-postgresql

## Background
[AWS Lambda](https://aws.amazon.com/lambda/) function that imports JSON data to a PostgreSQL database on [RDS](https://aws.amazon.com/rds/) in response to an [Amazon S3 event notification](https://aws.amazon.com/rds/).  A typical event triggering a notification in this case would be creating (upload, copy or write) a JSON file in an S3 bucket.

This function will:
1. Create a table in PostgreSQL called `json_table` with a `data` column of data type `jsonb`.  This is obviously the field where JSON data will be inserted.
2. Insert data into `json_table`.
3. Create an SNS topic called `message-from-lambda` if it doesn't already exist.
4. Publish a message to the topic whenever the function is invoked.

- <sub>Just comment or remove SNS code if you don't want a to use that service.</sub>

## Requirements
- [AWS CLI](https://aws.amazon.com/cli/)
- PostgreSQL 11+ on RDS associated with an IAM role with [s3Import feature](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Procedural.Importing.html#USER_PostgreSQL.S3Import)
- Python 3.6+
- An [IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) for the Lambda function with sufficient permission to access S3, RDS and SNS. (Attaching the "full access" managed policies for those services can be used initially to get the function working.  You can customize policies to enforce "least privledge" later on.)

## Set up
1. Clone this repo

2. From a command prompt, go to the root directory of this project and create and activate a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/) 
```
$ python3 -m venv env
$ . env/bin/activate
```

3. Install dependencies
```
$ pip install -r requirements.txt
```

4. Update the `src/database.cfg` file with information for your PostgreSQL instance on RDS.  For example:
```
[RDS]
HOST=dbidentifer.abcefghijklm.us-west-2.rds.amazonaws.com
DB_NAME=postgres
DB_USER=username
DB_PWD=password
```

5. Modify `template.yaml` with the ARN for your Lambda IAM role. 

6. In `command.sh`, modify the `--s3-bucket` parameter value of hte `aws cloudformation package` command with the name of your S3 bucket where the Lambda package should be uploaded.

7. From `command.sh` execute the commands under "zip dependencies from virtualenv and source files" which will create the `lambda.zip` deployment package in the `src` directory.

8. Also from `command.sh` execute the package and deploy cloudformation commands.  This will create the Lambda function on AWS.

9. For the S3 bucket where JSON files will be created, [configue an event notification](https://docs.aws.amazon.com/AmazonS3/latest/dev/NotificationHowTo.html) that will publish a message to the Lambda function (`S3toRdsLambda-ImportToRDS...`).  To respond to JSON file uploads, the "Put" event should be configured.

10. Upload a JSON file to your bucket and check the `json_table` for the inserted record.