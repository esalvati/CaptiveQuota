# Serviço de bloqueio FortiGate de 2 horas

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
	- registra ou atualiza a sessão do cliente (usa o IP da requisição se `?ip=` não for fornecido).
	- retorna JSON `{permitido: true|false, motivo, primeiro_acesso, decorrido, tempo_limite}`.
- `GET /health`
	- retorna `ok`.

Nota de integração:
Substitua `%%BLOCKER_URL%%` em `disclaimer-SIM.html` pela URL pública deste serviço (por exemplo `https://auth.example.com`).\
A página de termo de consentimento deve passar o IP fornecido pelo FortiGate como `?ip=%%SOURCE_IP%%` para `/status`, para que o serviço rastreie o endereço correto do cliente.
