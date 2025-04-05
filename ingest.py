import json
import streamlit as st
import boto3

aws_access_key = st.secrets["aws"]["aws_access_key"]
aws_secret_key = st.secrets["aws"]["aws_secret_key"]

def s3_fetch_file(s3_key, bucket="grafluence"):
    s3_client = boto3.client(
        "s3",
        region_name="us-east-1",  # ✅ or whatever region your bucket is in
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )

    try:
        obj = s3_client.get_object(Bucket=bucket, Key=s3_key)
        body = obj["Body"].read().decode("utf-8")
        return json.loads(body)
    except Exception as e:
        print(f"Error fetching {s3_key}: {e}")
        return {}

# def generate_signed_url(s3_key, bucket="grafluence", expires_in=3600):
#     s3_client = boto3.client(
#         "s3",
#         aws_access_key_id=aws_access_key,
#         aws_secret_access_key=aws_secret_key
#     )
#     return s3_client.generate_presigned_url(
#         "get_object",
#         Params={"Bucket": bucket, "Key": s3_key},
#         ExpiresIn=expires_in
#     )
