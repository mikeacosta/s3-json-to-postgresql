# zip dependencies from virtualenv and source files
rm src/lambda.zip
cd env/lib/python3.6/site-packages/
zip -r9 ../../../../src/lambda.zip *
cd ../../../../src/
zip -g lambda.zip sql_queries.py lambda_function.py database.cfg
cd ..

# package cloudformation
aws cloudformation package --s3-bucket bucket-name-for-package \
    --template-file template.yaml \
    --output-template-file gen/template-generated.yaml

# deploy cloudformation
aws cloudformation deploy \
    --template-file gen/template-generated.yaml \
    --stack-name S3toRdsLambda \
    --capabilities CAPABILITY_IAM

# delete stack
aws cloudformation delete-stack --stack-name S3toRdsLambda