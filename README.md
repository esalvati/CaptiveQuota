# Serviço de bloqueio de disclaimer para FortiGate

Este serviço rastreia IPs de clientes e aplica um limite de sessão de 2 horas a partir da primeira aceitação no dia.

```bash
# Construir a imagem
podman build -t fortigate-blocker:latest ./service

# Executar o contêiner (mapear porta e persistir o banco em ./data)
mkdir -p data
podman run --rm -p 8000:8000 -v "$(pwd)/data:/data" fortigate-blocker:latest
```

Endpoints:
- `GET /status`
	- registra ou atualiza a sessão do cliente (usa `cliente_src` se fornecido, caso contrário usa o endereço remoto da requisição).
	- retorna JSON `{permitido: true|false, motivo, primeiro_acesso, decorrido, tempo_limite, cliente_src, fgt_hostname}`.
- `GET /health`
	- retorna `ok`.

Nota de integração:
Substitua `%%BLOCKER_URL%%` na página de disclaimer pela URL pública deste serviço (por exemplo `https://auth.example.com`).\\
A página de termo de consentimento deve passar o identificador do cliente e o hostname do FortiGate como `?cliente_src=%%SOURCE_IP%%&fgt_hostname=%%FGT_HOSTNAME%%` para `/status`, para que o serviço rastreie corretamente o cliente e o host FortiGate.
