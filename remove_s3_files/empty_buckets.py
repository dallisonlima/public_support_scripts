#!/usr/bin/env python3
import os
import sys

import boto3
from botocore.exceptions import ClientError

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

BUCKETS = [
    "amz-bucket-dallison-teste"
]


def log(msg):
    print(msg, flush=True)


def bucket_exists(client, name):
    try:
        client.head_bucket(Bucket=name)
        return True
    except ClientError:
        return False


def abort_multipart_uploads(client, name):
    count = 0
    paginator = client.get_paginator("list_multipart_uploads")
    for page in paginator.paginate(Bucket=name):
        for upload in page.get("Uploads", []):
            count += 1
            if not DRY_RUN:
                client.abort_multipart_upload(
                    Bucket=name, Key=upload["Key"], UploadId=upload["UploadId"]
                )
    return count


def empty_bucket(bucket):
    if DRY_RUN:
        return sum(1 for _ in bucket.object_versions.all())

    deleted = 0
    for response in bucket.object_versions.delete():
        deleted += len(response.get("Deleted", []))
    return deleted


def main():
    session = boto3.Session(region_name=AWS_REGION)
    client = session.client("s3")
    s3 = session.resource("s3")

    log(f"Iniciando esvaziamento de buckets | região: {AWS_REGION}")
    log(f"Total de buckets: {len(BUCKETS)}")
    if DRY_RUN:
        log("Modo DRY RUN ativo — nenhum objeto será removido")

    success = skipped = failed = 0

    for name in BUCKETS:
        log(f"Processando bucket: {name}")

        if not bucket_exists(client, name):
            log("  AVISO: bucket não encontrado ou sem acesso — pulando")
            skipped += 1
            continue

        try:
            uploads = abort_multipart_uploads(client, name)
            if uploads:
                verb = "Encontrados" if DRY_RUN else "Abortados"
                log(f"  {verb} {uploads} multipart upload(s)")

            removed = empty_bucket(s3.Bucket(name))
            verb = "Removeria" if DRY_RUN else "Removidos"
            log(f"  {verb} {removed} objeto(s)/versão(ões)")
            log(f"  Bucket {name} {'analisado' if DRY_RUN else 'esvaziado'} com sucesso")
            success += 1
        except ClientError as exc:
            log(f"  ERRO ao esvaziar {name}: {exc}")
            failed += 1

    log(f"Concluído — sucesso: {success}, pulados: {skipped}, falhas: {failed}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
