# 📚 Estuda AI: Plataforma de Aprendizado com IA Generativa

[![Deploy on Railway](https://railway.app/button.svg)](https://estudaaion-production.up.railway.app/)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-Web-green)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-Messaging-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Cloudflare R2](https://img.shields.io/badge/Storage-Cloudflare_R2-f38020)

> **Status:** 🚀 Em Produção (Fase 2: Arquitetura Assíncrona e Escalável)
>
> **Demo:** [Acesse aqui](https://estudaaion-production.up.railway.app/)

## 💡 Visão Geral

O **Estuda AI** é uma plataforma SaaS educacional projetada para transformar materiais de estudo passivos (PDFs, DOCX) em ferramentas de aprendizado ativo. Utilizamos **LLMs (Large Language Models)** orquestrados via **LangChain** para:

1.  📄 **Sintetizar Conhecimento:** Gerar resumos didáticos e focados.
2.  🧠 **Testar Fixação:** Criar Quizzes de Múltipla Escolha (QCM) personalizados baseados no conteúdo.
3.  📊 **Feedback Inteligente:** Identificar lacunas de aprendizado instantaneamente.

---

## 🏗️ Arquitetura do Sistema (Cloud Native)

Este projeto evoluiu de um monolito simples para uma **Arquitetura Orientada a Eventos**, garantindo escalabilidade e tolerância a falhas.

### Fluxo de Dados:
1.  **Web App (Flask):** Recebe o upload do usuário e envia o arquivo diretamente para o **Cloudflare R2** (Object Storage).
2.  **Produtor:** O Flask registra o metadado no **PostgreSQL** e publica uma mensagem na fila do **RabbitMQ**.
3.  **Worker (Consumidor):** Um serviço Python isolado escuta a fila, baixa o arquivo do R2, processa com IA e salva os resultados no banco.

```mermaid
graph LR
    User[Usuário Mobile/Desktop] -->|Upload| Web[Flask Web App]
    Web -->|Armazena Arquivo| R2[Cloudflare R2]
    Web -->|Grava Metadado| DB[(PostgreSQL)]
    Web -->|Publica Tarefa| MQ[RabbitMQ]
    MQ -->|Consome Tarefa| Worker[AI Worker]
    Worker -->|Lê Arquivo| R2
    Worker -->|Salva Resultado| DB