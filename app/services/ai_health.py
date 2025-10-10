# app/services/ai_health.py
from app.integrations.deepseek import chat, DeepSeekError

def deepseek_healthcheck() -> dict:
    try:
        content = chat(
            [
                {"role": "system", "content": "Você é um verificador de saúde do serviço."},
                {"role": "user", "content": "Responda 'OK'."}
            ],
            temperature=0.0,
            timeout=10
        )
        ok = content.strip().upper().startswith("OK")
        return {"ok": ok, "model_reply": content if ok else "unexpected_reply"}
    except DeepSeekError as e:
        return {"ok": False, "error": e.public_msg, "detail": e.detail, "http_status": e.http_status}
