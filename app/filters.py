from __future__ import annotations
import json
from datetime import date, datetime, timedelta
import pytz
from pytz import timezone
from markupsafe import Markup, escape

def _coerce_dict(v):
    if isinstance(v, dict):
        return v
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return {}
    return {}

def asdict(v):
    return _coerce_dict(v)

def date_br(value):
    if isinstance(value, (date, datetime)):
        return value.strftime("%d/%m/%Y")
    return ""

def datetime_br(value):
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y") + " 00:00"
    return ""

def timesince(value, now=None):
    if not isinstance(value, datetime):
        return ""
    now = now or datetime.utcnow()
    delta: timedelta = now - value
    s = int(delta.total_seconds())
    if s < 60: return "agora"
    m = s // 60
    if m < 60: return f"há {m}min"
    h = m // 60
    if h < 24: return f"há {h}h"
    d = h // 24
    return f"há {d}d"

def kcals(v):
    try:
        iv = int(round(float(v)))
        return f"{iv:,}".replace(",", ".") + "\u202Fkcal"
    except Exception:
        return "-"

def grams(v):
    try:
        iv = int(round(float(v)))
        return f"{iv} g"
    except Exception:
        return "-"

def truncate_chars(s, n=120, suffix="…"):
    if not s: return ""
    s = str(s)
    return s if len(s) <= n else s[:n].rstrip() + suffix

def yesno(val, yes="Sim", no="Não", maybe="—"):
    if val is True: return yes
    if val is False: return no
    return maybe

def safejson(v, indent=2):
    try:
        txt = json.dumps(v, ensure_ascii=False, indent=indent)
    except Exception:
        txt = escape(str(v))
    return Markup(f"<pre class='mb-0 small'>{escape(txt)}</pre>")

def to_brazilian_time(dt):
    if not dt:
        return ''
    tz = timezone('America/Sao_Paulo')
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.UTC)
    return dt.astimezone(tz).strftime('%d/%m/%Y %H:%M')

def register_template_filters(app):
    filters = {
        "asdict": asdict,
        "date_br": date_br,
        "datetime_br": datetime_br,
        "timesince": timesince,
        "kcals": kcals,
        "grams": grams,
        "truncate_chars": truncate_chars,
        "yesno": yesno,
        "safejson": safejson,
        "to_brazilian_time": to_brazilian_time,
    }
    app.jinja_env.filters.update(filters)
