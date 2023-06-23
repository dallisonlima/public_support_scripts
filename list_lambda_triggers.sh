#!/bin/bash

# Obtem a lista de funções lambda
functions=$(aws lambda list-functions --query 'Functions[*].FunctionName' --output text)

# Itera sobre cada função lambda
for function in $functions
do
  # Obtem a política associada à função lambda
  policy=$(aws lambda get-policy --function-name $function --query 'Policy' --output text)
  
  # Extrai o valor de AWS:SourceArn do trigger utilizando o jq
  source_arn=$(echo $policy | jq -r '.Statement[].Condition.ArnLike["AWS:SourceArn"]')
  
  # Exibe o resultado
  echo "Função Lambda: $function"
  echo "AWS:SourceArn: $source_arn"
  echo
done
