import os
import subprocess

def percorrer_diretorios(pasta):
    for diretorio_raiz, diretorios, arquivos in os.walk(pasta):
        if ".terraform-docs.yml" in arquivos:
            comando = f"terraform-docs -c .terraform-docs.yml . > README.md"
            
            subprocess.run(comando, shell=True, check=True, cwd=diretorio_raiz)
            print(f"Comando executado em: {diretorio_raiz}")

pasta_raiz = "."
percorrer_diretorios(pasta_raiz)
