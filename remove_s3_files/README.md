# empty_buckets

Script Python para esvaziar buckets S3.

Remove todos os objetos e versões de cada bucket configurado, incluindo aborto de multipart uploads pendentes. Útil antes de recriar ou destruir infraestrutura de static frontend via Terraform.

## Pré-requisitos

- Python 3.8+
- Credenciais AWS configuradas (profile, SSO ou variáveis de ambiente) com permissão de leitura e exclusão nos buckets alvo
- Dependência: `boto3`

```bash
pip install boto3
```

## Configuração

Edite a lista `BUCKETS` em `empty_buckets.py` com os nomes dos buckets a esvaziar:

```python
BUCKETS = [
    "amz-bucket-dallison-teste",
    # amz-bucket-new-1,
    # amz-bucket-new-2
]
```

Variáveis de ambiente opcionais:

| Variável     | Padrão       | Descrição                                      |
|--------------|--------------|------------------------------------------------|
| `AWS_REGION` | `us-east-1`  | Região dos buckets                               |
| `DRY_RUN`    | `false`      | Se `true`, apenas simula sem remover objetos   |

## Uso

### Simulação (recomendado antes de executar)

```bash
DRY_RUN=true python empty_buckets.py
```

### Execução real

```bash
python empty_buckets.py
```

Com profile AWS específico:

```bash
AWS_PROFILE=ecomm-dev python empty_buckets.py
```

Com região customizada:

```bash
AWS_REGION=us-east-1 DRY_RUN=true python empty_buckets.py
```

## O que o script faz

Para cada bucket na lista:

1. Verifica se o bucket existe e se há acesso (`head_bucket`)
2. Aborta multipart uploads pendentes
3. Remove todas as versões de objetos (`object_versions.delete()`), incluindo delete markers em buckets versionados
4. Registra o resultado e segue para o próximo bucket

Buckets inexistentes ou sem permissão são **pulados** com aviso, sem interromper o restante.

## Saída e exit code

- **0** — todos os buckets processados com sucesso (ou pulados por inexistência)
- **1** — ao menos um bucket falhou durante a exclusão

Exemplo de saída:

```
Iniciando esvaziamento de buckets | região: us-east-1
Total de buckets: 1
Processando bucket: amz-bucket-dallison-teste
  Removidos 42 objeto(s)/versão(ões)
  Bucket amz-bucket-dallison-teste esvaziado com sucesso
Concluído — sucesso: 1, pulados: 0, falhas: 0
```

## Permissões IAM necessárias

No mínimo, para cada bucket alvo:

- `s3:ListBucket`
- `s3:ListBucketVersions`
- `s3:DeleteObject`
- `s3:DeleteObjectVersion`
- `s3:AbortMultipartUpload`
- `s3:ListMultipartUploadParts`

## Atenção

- **A exclusão é irreversível** (exceto se o bucket tiver Object Lock ou replicação externa)
- Sempre rode com `DRY_RUN=true` primeiro para validar a lista de buckets e a contagem de objetos
- O script **não remove o bucket**, apenas esvazia o conteúdo
- Buckets com versionamento habilitado terão todas as versões removidas
