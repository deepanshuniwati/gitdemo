import aws_cdk.core as cdk
import aws_cdk.aws_s3 as s3

class MyStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket
        my_bucket = s3.Bucket(self, "MyBucket")

        # Output the bucket URL
        cdk.CfnOutput(self, "BucketUrl", value=my_bucket.bucket_website_url)

app = cdk.App()
MyStack(app, "my_stack")
app.synth()=