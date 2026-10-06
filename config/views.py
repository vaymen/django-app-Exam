import platform
import socket

import django
from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.utils.html import escape

PAGE = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Django با موفقیت نصب شد</title>
<style>
  :root {{ --bg:#0c4b33; --bg2:#092e20; --ok:#34d399; --bad:#f87171; --card:#ffffff; --ink:#0f172a; --mute:#64748b; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; min-height:100vh; font-family: Vazirmatn, Tahoma, "Segoe UI", sans-serif; color:var(--ink);
         background: radial-gradient(1200px 600px at 80% -10%, #1f7a55 0%, transparent 60%),
                     linear-gradient(160deg, var(--bg), var(--bg2)); display:flex; align-items:center; justify-content:center; padding:24px; }}
  main {{ width:100%; max-width:860px; }}
  .hero {{ text-align:center; color:#fff; margin-bottom:28px; }}
  .rocket {{ font-size:64px; display:inline-block; animation: float 3s ease-in-out infinite; }}
  @keyframes float {{ 50% {{ transform: translateY(-10px); }} }}
  h1 {{ margin:8px 0 6px; font-size:clamp(26px,5vw,40px); }}
  .hero p {{ margin:0; opacity:.85; font-size:17px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:14px; margin-bottom:18px; }}
  .card {{ background:var(--card); border-radius:16px; padding:18px 20px; box-shadow:0 10px 30px rgba(0,0,0,.25); }}
  .card small {{ color:var(--mute); display:block; margin-bottom:6px; font-size:13px; }}
  .card b {{ font-size:18px; word-break:break-all; }}
  .pill {{ display:inline-flex; align-items:center; gap:8px; }}
  .dot {{ width:11px; height:11px; border-radius:50%; background:var(--c); box-shadow:0 0 0 4px color-mix(in srgb, var(--c) 25%, transparent); }}
  .links {{ display:flex; flex-wrap:wrap; gap:10px; justify-content:center; margin-top:8px; }}
  .links a {{ color:#fff; text-decoration:none; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.25);
              padding:10px 18px; border-radius:999px; font-size:15px; transition:.2s; }}
  .links a:hover {{ background:rgba(255,255,255,.25); }}
  footer {{ text-align:center; color:rgba(255,255,255,.6); font-size:13px; margin-top:22px; }}
  code {{ direction:ltr; unicode-bidi:embed; }}
</style>
</head>
<body>
<main>
  <section class="hero">
    <div class="rocket">🚀</div>
    <h1>نصب Django با موفقیت انجام شد!</h1>
    <p>برنامه در حال اجراست و آمادهٔ استفاده است.</p>
  </section>

  <section class="grid">
    <div class="card"><small>وضعیت پایگاه‌داده (PostgreSQL)</small>
      <span class="pill" style="--c:{db_color}"><span class="dot"></span><b>{db_text}</b></span></div>
    <div class="card"><small>نسخهٔ برنامه (تگ ایمیج)</small><b><code>{app_version}</code></b></div>
    <div class="card"><small>نام Pod / کانتینر</small><b><code>{host}</code></b></div>
    <div class="card"><small>نسخهٔ Django</small><b><code>{django_version}</code></b></div>
    <div class="card"><small>نسخهٔ Python</small><b><code>{python_version}</code></b></div>
    <div class="card"><small>حالت DEBUG</small><b>{debug}</b></div>
  </section>

  <nav class="links">
    <a href="/healthz">/healthz · زنده بودن</a>
    <a href="/readyz">/readyz · آمادگی و اتصال به دیتابیس</a>
    <a href="https://docs.djangoproject.com/en/{docs}/" target="_blank" rel="noopener">مستندات Django</a>
  </nav>
  <footer>با هر بار رفرش، اگر چند Pod داشته باشید ممکن است «نام Pod» تغییر کند؛ نشانهٔ کارکرد load balancing.</footer>
</main>
</body>
</html>
"""


def _db_ok():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001 - any failure means "not connected"
        return False


def welcome(request):
    ok = _db_ok()
    html = PAGE.format(
        db_color="#34d399" if ok else "#f87171",
        db_text="متصل ✓" if ok else "قطع ✗",
        app_version=escape(settings.APP_VERSION),
        host=escape(socket.gethostname()),
        django_version=django.get_version(),
        python_version=platform.python_version(),
        debug="روشن" if settings.DEBUG else "خاموش",
        docs=".".join(django.get_version().split(".")[:2]),
    )
    return HttpResponse(html)
