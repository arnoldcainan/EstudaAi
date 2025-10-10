# 📚 Estuda AI: Domine Qualquer Assunto com Inteligência Artificial

**Status do Projeto:** Fase 1: MVP Monolítico (Flask + LangChain Interno)

## 💡 Visão Geral e Proposta de Valor

O Estuda AI é uma plataforma educacional que transforma documentos brutos (PDF, DOCX) em materiais de estudo de alta qualidade, utilizando Modelos de Linguagem para:
1.  Gerar **Resumos Focados** de longos documentos.
2.  Criar **Testes de Múltipla Escolha (QCM)** personalizados.
3.  Fornecer **Feedback Preditivo** sobre os tópicos que exigem mais atenção.

## ⚙️ Tecnologias Principais

| Categoria | Tecnologia | Justificativa no Projeto |
| :--- | :--- | :--- |
| **Backend/Web** | Python, Flask, Jinja2 | Rota web e interface de usuário. |
| **Inteligência Artificial** | **LangChain** | Orquestração do LLM para encadeamento de tarefas (Resumo -> QCM). |
| **Arquitetura** | **RabbitMQ** (Futuro) | Fila de tarefas para processamento de IA confiável e garantia de entrega. |
| **Arquitetura** | **Kafka** (Futuro) | Event streaming para notificações de status em tempo real. |

## 🚀 Roadmap e Evolução (Fases do Projeto)

O projeto está em desenvolvimento com foco na refatoração de um monolito para uma arquitetura de microsserviços.

| Fase | Foco | Status |
| :--- | :--- | :--- |
| **Fase 1 (Atual)** | **MVP Monolítico.** Upload e processamento de LangChain síncrono. | ✅ Completo (Lógica básica de IA) |
| **Fase 2** | **Desacoplamento de Tarefas.** Migração do processamento da IA para um **`AIWorker`** e integração com **RabbitMQ**. | ⏳ Em desenvolvimento |
| **Fase 3** | **Comunicação em Tempo Real.** Implementação do **Kafka** para transmitir o status "Estudo Pronto" ao frontend. | ⚪️ Planejado |

## 🛠️ Como Rodar o Projeto (MVP Monolítico)

*(Deixe esta seção para depois. Por enquanto, aponte para o `app.py`)*

1. Clone o repositório: `git clone [URL]`
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute: `python app.py`

---

**Próximo Passo:** Com o `README` em rascunho, vamos começar a codificar a **Rota de Upload** (`/novo_estudo`).
