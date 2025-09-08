# api_sms_final_v11_fire-and-forget.py
from flask import Flask, request, jsonify
import subprocess
import os
import time
import threading

# --- CONFIGURAÇÕES ---
API_TOKEN_ESPERADO = os.environ.get("SMS_API_TOKEN", "SEU_TOKEN_SUPER_SECRETO_AQUI")
GAMMU_CONFIG_FILE = "/root/.gammurc"
MAX_TENTATIVAS_ERRO_GERAL = 5 
ESPERA_ENTRE_TENTATIVAS = 10
ESPERA_INICIAL_69 = 5
ESPERA_MAXIMA_69 = 60
# --------------------------------------------------------

app = Flask(__name__)

# --- TODA A LÓGICA DE ENVIO AGORA ESTÁ NESTA FUNÇÃO SEPARADA ---
# Ela será executada em segundo plano e não retornará nada para o cliente.
# Todo o feedback será dado via 'print' no console do servidor.
def tarefa_enviar_sms(numero, mensagem):
    """
    Esta é a tarefa que roda em segundo plano (thread).
    Ela verifica a rede e depois entra no loop de envio até ter sucesso ou falha permanente.
    """
    # ETAPA 1: VERIFICAR A PRONTIDÃO DA REDE
    tentativa_check = 0
    comando_check = ['/usr/bin/gammu', '-c', GAMMU_CONFIG_FILE, 'networkinfo']
    print(f"[Thread para {numero}] --- VERIFICANDO PRONTIDÃO DA REDE ---")
    while True:
        tentativa_check += 1; print(f"[Thread para {numero}] Verificação de rede, tentativa {tentativa_check}...")
        try:
            resultado = subprocess.run(comando_check, capture_output=True, text=True, check=True, timeout=20)
            if "Home network" in resultado.stdout:
                print(f"[Thread para {numero}] ✅ Rede OK! Modem registrado.")
                break # Sai do loop de verificação e continua para o envio
            else:
                print(f"[Thread para {numero}] Rede ainda não registrada. Aguardando..."); time.sleep(10)
        except Exception as e:
            detalhe_erro = e.stderr if hasattr(e, 'stderr') else str(e); print(f"[Thread para {numero}] Erro ao verificar a rede: {detalhe_erro}")
            if tentativa_check > 3:
                print(f"❌ FALHA PERMANENTE: [Thread para {numero}] Modem não registrou na rede. Desistindo da tarefa. Erro: {detalhe_erro}")
                return # Encerra a thread
            time.sleep(10)

    # ETAPA 2: ENVIAR O SMS COM A LÓGICA DE RETENTATIVA
    print(f"\n[Thread para {numero}] --- INICIANDO PROCESSO DE ENVIO ---")
    comando_envio = ['/usr/bin/gammu', '-c', GAMMU_CONFIG_FILE, 'sendsms', 'TEXT', numero, '-text', mensagem]
    tentativa_total = 0
    tentativas_erro_geral_consecutivas = 0
    tempo_de_espera_69 = ESPERA_INICIAL_69

    while True:
        tentativa_total += 1
        comando_str = ' '.join(comando_envio)
        print(f"\n[Thread para {numero}] [Tentativa Total {tentativa_total}] Executando:\n{comando_str}")
        try:
            subprocess.run(comando_envio, capture_output=True, text=True, check=True, timeout=45)
            print(f"✅ SUCESSO: [Thread para {numero}] SMS enviado na tentativa {tentativa_total}.")
            return # Encerra a thread com sucesso
        except subprocess.CalledProcessError as e:
            if "error 69" in e.stderr.lower():
                print(f"⚠️ [Thread para {numero}] Detectado 'error 69'. Aguardando {tempo_de_espera_69}s para retentativa infinita...")
                time.sleep(tempo_de_espera_69)
                tempo_de_espera_69 = min(tempo_de_espera_69 * 2, ESPERA_MAXIMA_69)
                tentativas_erro_geral_consecutivas = 0
                continue
            else:
                tentativas_erro_geral_consecutivas += 1
                print(f"⚠️ [Thread para {numero}] Erro genérico. Tentativa de reenvio {tentativas_erro_geral_consecutivas}/{MAX_TENTATIVAS_ERRO_GERAL}.")
                print(f"   Erro reportado: {e.stderr.strip()}")
                if tentativas_erro_geral_consecutivas >= MAX_TENTATIVAS_ERRO_GERAL:
                    print(f"❌ FALHA PERMANENTE: [Thread para {numero}] Limite de tentativas atingido. Erro final: {e.stderr.strip()}")
                    return # Encerra a thread com falha
                else:
                    time.sleep(ESPERA_ENTRE_TENTATIVAS)
                    continue
        except Exception as e:
            print(f"❌ FALHA CRÍTICA: [Thread para {numero}] Erro no script: {e}")
            return # Encerra a thread com falha

# --- ROTA DA API (ENDPOINT) ---
# Agora esta função é muito mais simples e rápida.
@app.route('/enviar-sms', methods=['POST'])
def enviar_sms():
    dados = request.get_json()
    if not dados: return jsonify({"status": "erro", "mensagem": "JSON inválido."}), 400
    token, numero, mensagem = dados.get('token'), dados.get('numero'), dados.get('mensagem')
    if not token or token != API_TOKEN_ESPERADO: return jsonify({"status": "erro", "mensagem": "Token inválido."}), 403
    if not numero or not mensagem: return jsonify({"status": "erro", "mensagem": "Campos obrigatórios ausentes."}), 400

    # Cria uma nova thread para executar a tarefa de envio em segundo plano
    thread = threading.Thread(target=tarefa_enviar_sms, args=(numero, mensagem))
    # Inicia a thread
    thread.start()

    # Retorna uma resposta IMEDIATA para o cliente, confirmando o recebimento.
    print(f"API: Requisição para {numero} recebida e enfileirada. Tarefa em segundo plano iniciada.")
    return jsonify({
        "status": "aceito",
        "mensagem": "SMS recebido e enfileirado para envio."
    }), 202  # 202 Accepted é o código HTTP correto para este tipo de operação

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "API de SMS (v11 - Fire and Forget) online"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)