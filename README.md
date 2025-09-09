# Resilient SMS API with Gammu and Python

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.x-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Gammu](https://img.shields.io/badge/Gammu-SMS%20Gateway-orange)


## 📑 Table of Contents
- [English Version](#english-version)  
  - [Features](#features)  
  - [Prerequisites](#prerequisites)  
  - [Installation](#installation)  
  - [How to Use](#how-to-use)  
  - [Expected Response](#expected-response)  
  - [Monitoring](#monitoring)  
- [Versão em Português](#versão-em-português)  
  - [Funcionalidades](#funcionalidades)  
  - [Pré-requisitos](#pré-requisitos)  
  - [Instalação](#instalação)  
  - [Como Usar](#como-usar)  
  - [Resposta Esperada](#resposta-esperada)  
  - [Monitoramento](#monitoramento)  

---

## English Version

This is a simple yet robust API built with Flask (Python) to serve as a bridge for a Gammu modem, allowing for asynchronous and network-failure-resilient SMS sending.

### Features
- **Single and Secure Endpoint**: A single `/enviar-sms` endpoint protected by a static token.  
- **"Fire and Forget" Model**: The API responds immediately with a `202 Accepted` status, while the sending process is handled in the background (using threading).  
- **Network Readiness Check**: Before attempting to send, the script verifies that the modem is properly registered with the carrier's network, preventing failures due to incomplete initialization.  
- **Intelligent and Persistent Retry Logic**:  
  - Indefinitely retries in case of an error 69 (network failure).  
  - Retries a limited number of times for other sending errors, avoiding infinite loops on permanent failures.  
- **Console Monitoring**: The entire lifecycle of a message send (verification, attempts, success, failure) is logged to the server console for easy monitoring.  

### Prerequisites
- A Linux server (Debian, Ubuntu, CentOS, etc.).  
- Python 3.  
- Gammu installed, configured (`.gammurc`), and functional via the command line.  
- A USB modem (3G/4G dongle) with a SIM card with the PIN request disabled.  
- Power management disabled via `/etc/modprobe.d`.  
- If your modem emulates a flash drive and a USB modem, disable `usb_storage` by blacklisting it via `/etc/modprobe`.
- FreeBSD is supported

### Installation
Clone this repository:

```bash
git clone https://github.com/maurognx/api-sms-gammu.git
cd api-sms-gammu
```

Install the Python dependencies:

```bash
pip install Flask
```

Configure the `api_gammu.py` script: Open the file and edit the following variables at the top:

- `API_TOKEN_ESPERADO`: Set a strong secret token.  
- `GAMMU_CONFIG_FILE`: Confirm that the path to your `.gammurc` file is correct.  

Run the API: It is recommended to run as root or a user belonging to the `dialout` group.

```bash
sudo python3 api_gammu.py
```

### How to Use
Send a POST request to the `/enviar-sms` endpoint with a JSON body containing the token, number, and message.

Example with curl:

```bash
curl -X POST http://ipofyourserver:5000/enviar-sms \
-H "Content-Type: application/json" \
-d '{
    "token": "YOUR_SUPER_SECRET_TOKEN_HERE",
    "numero": "123456789",
    "mensagem": "Your test message here!"
}'
```

### Expected Response
If the request is valid, the API will respond immediately with the following, indicating that the message has been received and is queued for sending:

```json
{
  "status": "accepted",
  "mensagem": "SMS received and queued for sending."
}
```

### Monitoring
The actual sending status (attempts, success, or failure) should be monitored via the console (standard output) where the Python script is running.

---

## Versão em Português

API de SMS Resiliente com Gammu e Python

Esta é uma API simples, porém robusta, construída com Flask (Python) para servir como uma ponte para um modem Gammu, permitindo o envio de SMS de forma assíncrona e resiliente a falhas de rede.

### Funcionalidades
- **Endpoint Único e Seguro**: Um único endpoint `/enviar-sms` protegido por um token estático.  
- **Modelo "Disparar e Esquecer" (Fire and Forget)**: A API responde imediatamente com status `202 Accepted`, enquanto o envio é processado em segundo plano (usando threading).  
- **Verificação de Prontidão da Rede**: Antes de tentar enviar, o script verifica se o modem está devidamente registrado na rede da operadora, evitando falhas por inicialização incompleta.  
- **Retentativa Inteligente e Persistente**:  
  - Tenta reenviar indefinidamente em caso de erro 69 (falha de rede).  
  - Tenta reenviar um número limitado de vezes para outros erros de envio, evitando loops infinitos em falhas permanentes.  
- **Monitoramento via Console**: Todo o ciclo de vida do envio de uma mensagem (verificação, tentativas, sucesso, falha) é logado no console do servidor para fácil monitoramento.  

### Pré-requisitos
- Um servidor Linux (Debian, Ubuntu, CentOS, etc.).  
- Python 3.  
- Gammu instalado, configurado (`.gammurc`) e funcional via linha de comando.  
- Um modem USB (dongle 3G/4G) com um chip (SIM card) com o pedido de PIN desativado.  
- Gerenciamento de energia desligado via `/etc/modprobe.d`.  
- Se seu modem emula um pendrive e também modem USB, desligue o `usb_storage` ativando a blacklist via `/etc/modprobe`.
- FreeBSD é suportado

### Instalação
Clone este repositório:

```bash
git clone https://github.com/maurognx/api-sms-gammu.git
cd api-sms-gammu
```

Instale as dependências do Python:

```bash
pip install Flask
```

Configure o script `api_gammu.py`: Abra o arquivo e edite as seguintes variáveis no topo:

- `API_TOKEN_ESPERADO`: Defina um token secreto forte.  
- `GAMMU_CONFIG_FILE`: Confirme se o caminho para o seu arquivo `.gammurc` está correto.  

Execute a API: Recomenda-se rodar como root ou um usuário que pertença ao grupo `dialout`.

```bash
sudo python3 api_gammu.py
```

### Como Usar
Envie uma requisição POST para o endpoint `/enviar-sms` com um corpo JSON contendo o token, o número e a mensagem.

Exemplo com curl:

```bash
curl -X POST http://IP_DO_SEU_SERVIDOR:5000/enviar-sms \
-H "Content-Type: application/json" \
-d '{
    "token": "SEU_TOKEN_SUPER_SECRETO_AQUI",
    "numero": "123456789",
    "mensagem": "Sua mensagem de teste aqui!"
}'
```

### Resposta Esperada
Se a requisição for válida, a API responderá imediatamente com o seguinte, indicando que a mensagem foi recebida e está na fila para ser enviada:

```json
{
  "status": "aceito",
  "mensagem": "SMS recebido e enfileirado para envio."
}
```

### Monitoramento
O status real do envio (tentativas, sucesso ou falha) deve ser acompanhado pelo console (saída padrão) onde o script Python está rodando.


