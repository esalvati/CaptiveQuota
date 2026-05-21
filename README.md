# Serviço de bloqueio FortiGate de 2 horas

Este serviço rastreia IPs de clientes e aplica um limite de sessão de 2 horas a partir da primeira aceitação no dia.

Início rápido (construir e executar com Podman):

```bash
# Construir a imagem
podman build -t fortigate-blocker:latest ./service

# Executar o contêiner (mapear porta e persistir o banco em ./data)
mkdir -p data
podman run --rm -p 8000:8000 -v "$(pwd)/data:/data" fortigate-blocker:latest
```

Observação: usuários do Docker CLI ainda podem usar os comandos `docker` mostrados anteriormente; `podman` é um substituto compatível na maioria dos ambientes.

Endpoints:
- `GET /status`
	- registra ou atualiza a sessão do cliente (usa o IP da requisição se `?ip=` não for fornecido).
	- retorna JSON `{allowed: true|false, first_access, elapsed, limit_seconds}`.
- `GET /health`
	- retorna `ok`.

Nota de integração:
Substitua `%%BLOCKER_URL%%` em `disclaimer-SIM.html` pela URL pública deste serviço (por exemplo `https://auth.example.com`). A página de termo deve passar o IP fornecido pelo FortiGate como `?ip=%%SOURCE_IP%%` para `/accept` e `/status`, para que o serviço rastreie o endereço correto do cliente.
