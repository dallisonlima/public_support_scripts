#!/bin/bash

# Verifica se o namespace foi passado como argumento
if [ -z "$1" ]; then
  echo "Uso: $0 <NOME_DO_NAMESPACE>"
  exit 1
fi

NAMESPACE="$1"

# 1. Adiciona o cabeçalho CSV na primeira linha
echo "NOME_DEPLOYMENT,MIN_PODS,MAX_PODS,CPU_REQUEST,CPU_LIMIT,MEMORY_REQUEST,MEMORY_LIMIT"

# 2. Execução do comando principal
# Lista todos os deployments e itera sobre eles
kubectl get deployments -n "$NAMESPACE" -o name 2>/dev/null | sed 's/deployment.apps\///' | xargs -I {} sh -c '
    DEPLOYMENT_NAME="{}"
    NS_ARG="'"$NAMESPACE"'"

    # 3. Busca HPA por filtragem LOCAL (Necessário pois field selector é inválido)
    # Obtém todos os HPAs e usa jq para encontrar o correspondente
    HPA_INFO=$(kubectl get hpa -n "$NS_ARG" -o json 2>/dev/null | jq -c "
        .items[] | select(.spec.scaleTargetRef.name == \"$DEPLOYMENT_NAME\")
    " 2>/dev/null)

    if [ -z "$HPA_INFO" ]; then
        # HPA não encontrado: usa replicas do Deployment para MIN_PODS
        MIN_PODS=$(kubectl get deploy $DEPLOYMENT_NAME -n "$NS_ARG" -o jsonpath="{.spec.replicas}" 2>/dev/null || echo "-")
        MAX_PODS="-"
    else
        # HPA encontrado: extrai min/maxReplicas
        MIN_PODS=$(echo "$HPA_INFO" | jq -r ".spec.minReplicas // \"-\"")
        MAX_PODS=$(echo "$HPA_INFO" | jq -r ".spec.maxReplicas // \"-\"")
    fi

    # 4. Obtém as informações de recursos do Deployment
    DEPLOYMENT_JSON=$(kubectl get deploy $DEPLOYMENT_NAME -n "$NS_ARG" -o json 2>/dev/null)

    if [ -n "$DEPLOYMENT_JSON" ]; then
        # Formata a saída em CSV
        echo "$DEPLOYMENT_JSON" | jq -r --arg min "$MIN_PODS" --arg max "$MAX_PODS" --arg deploy_name "$DEPLOYMENT_NAME" "
        .spec.template.spec.containers[] | [
            \$deploy_name,
            \$min,
            \$max,
            # CPU Requests
            (.resources.requests.cpu // \"-\"),
            # CPU Limits
            (.resources.limits.cpu // \"-\"),
            # Memory Requests
            (.resources.requests.memory // \"-\"),
            # Memory Limits
            (.resources.limits.memory // \"-\")
        ] | join(\",\")"
    fi
'
