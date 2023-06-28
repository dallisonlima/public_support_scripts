import re
# Gere o texto com os comandos ->  terraform plan -out=tfplan && terraform show -no-color tfplan > tfplan.json
# Texto fornecido
texto = '''
  # module.route_53_record_sample["teste1.com.br"].aws_route53_record.default["record1"] will be created
  + resource "aws_route53_record" "default" {
      + allow_overwrite = (known after apply)
      + fqdn            = (known after apply)
      + id              = (known after apply)
      + name            = "teste1.com.br"
      + type            = "A"
      + zone_id         = "Z012345678890F"

      + alias {
          + evaluate_target_health = true
          + name                   = "dualstack.alb-teste-123.us-east-1.elb.amazonaws.com"
          + zone_id                = "Z123123123123"
        }
    }

  # module.route_53_record_sample["teste2.com.br"].aws_route53_record.default["record1"] will be created
  + resource "aws_route53_record" "default" {
      + allow_overwrite = (known after apply)
      + fqdn            = (known after apply)
      + id              = (known after apply)
      + name            = "www.teste2.com.br"
      + type            = "CNAME"
      + zone_id         = "ZASKJDNASKJDNASKDF"

      + alias {
          + evaluate_target_health = true
          + name                   = "dualstack.alb-teste2-123456789.us-east-1.elb.amazonaws.com"
          + zone_id                = "ZASKDBASDHBASF"
        }
    }'''

# Padrões de expressão regular
padrao_caminho_recurso = r'module\.route_53_record_sample\["([^"]+)"\]\.aws_route53_record\.default\["([^"]+)"\]'
padrao_nome = r'name\s+= "(.*?)"'
padrao_tipo = r'type\s+= "(.*?)"'
padrao_zone_id = r'zone_id\s+= "(.*?)"'

# Encontrar todas as ocorrências de caminho_recurso no texto
matches_caminho_recurso = re.findall(padrao_caminho_recurso, texto)

for match_caminho_recurso in matches_caminho_recurso:
    caminho_recurso = 'module.route_53_record_sample["' + match_caminho_recurso[0] + '"].aws_route53_record.default["' + match_caminho_recurso[1] + '"]'

    # Encontrar o nome
    padrao_nome_recurso = re.compile(rf'{re.escape(caminho_recurso)}.*?name\s+=\s+"(.*?)"', re.DOTALL)
    match_nome = re.search(padrao_nome_recurso, texto)
    if match_nome:
        nome = match_nome.group(1)
    else:
        nome = None

    # Encontrar o tipo
    padrao_tipo_recurso = re.compile(rf'{re.escape(caminho_recurso)}.*?type\s+=\s+"(.*?)"', re.DOTALL)
    match_tipo = re.search(padrao_tipo_recurso, texto)
    if match_tipo:
        tipo = match_tipo.group(1)
    else:
        tipo = None

    # Encontrar o zone_id
    padrao_zone_id_recurso = re.compile(rf'{re.escape(caminho_recurso)}.*?zone_id\s+=\s+"(.*?)"', re.DOTALL)
    match_zone_id = re.search(padrao_zone_id_recurso, texto)
    if match_zone_id:
        zone_id = match_zone_id.group(1)
    else:
        zone_id = None

    # Criar o comando terraform import
    if caminho_recurso and nome and tipo and zone_id:
        comando_import = f'terraform import \'{caminho_recurso}\' {zone_id}_{nome}_{tipo}'
        print(comando_import)
    else:
        print("Não foi possível criar o comando terraform import.")
