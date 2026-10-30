param (
    [string]$Region = "us-east-1",
    [string]$StackName = "parcs-cluster"
)

$TemplatePath = Join-Path $PSScriptRoot "cloudformation.yaml"

if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    exit 1
}

aws cloudformation create-stack `
    --stack-name $StackName `
    --template-body "file://$TemplatePath" `
    --region $Region

aws cloudformation wait stack-create-complete --stack-name $StackName --region $Region

$dashboardUrl = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query "Stacks[0].Outputs[?OutputKey=='DashboardURL'].OutputValue" `
    --output text

Write-Host $dashboardUrl
