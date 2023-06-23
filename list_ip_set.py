import boto3

# Crie uma sessão do Boto3 usando as credenciais padrão do ambiente
session = boto3.Session()

# Crie um cliente para o serviço WAF
waf_client = session.client('wafv2')

# Nome do IPSet que você deseja obter
ip_set_name = 'exemplo'

# Função para obter o ID do IPSet
def get_ip_set_id(ip_set_name):
    # Obtenha a lista de IPSets disponíveis em todos os escopos
    response = waf_client.list_ip_sets(Scope='CLOUDFRONT')
    ip_sets = response['IPSets']

    while 'NextMarker' in response:
        response = waf_client.list_ip_sets(Scope='CLOUDFRONT', NextMarker=response['NextMarker'])
        ip_sets.extend(response['IPSets'])

    # Localize o IPSet específico que você deseja e obtenha o ID dele
    ip_set = next((ip for ip in ip_sets if ip['Name'] == ip_set_name), None)

    if ip_set:
        return ip_set['Id']
    else:
        return None

# Obtenha o ID do IPSet
ip_set_id = get_ip_set_id(ip_set_name)

if ip_set_id:
    # Use a função get_ip_set para obter informações detalhadas sobre o IPSet
    response = waf_client.get_ip_set(
        Name=ip_set_name,
        Scope='CLOUDFRONT',
        Id=ip_set_id
    )
    ip_set_info = response['IPSet']

    # Acesse a lista de IPs do IPSet
    ip_set_ips = ip_set_info['Addresses']

    # Imprima a lista de IPs
    for ip in ip_set_ips:
        print(ip)
else:
    print(f'O IPSet {ip_set_name} não foi encontrado.')
