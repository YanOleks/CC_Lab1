param (
    [string]$Region = "us-east-1",
    [string]$StackName = "parcs-cluster"
)

if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    exit 1
}

aws cloudformation delete-stack --stack-name $StackName --region $Region
aws cloudformation wait stack-delete-complete --stack-name $StackName --region $Region
