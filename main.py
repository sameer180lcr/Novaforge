from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import timedelta
import os, json, urllib.parse, urllib.request

app = Flask(__name__)
app.secret_key = "replace-this-in-production"
app.permanent_session_lifetime = timedelta(days=14)

# Optional demo booking link (replace with your Calendly)
DEMO_LINK = os.getenv("DEMO_LINK", "https://calendly.com/your-company/demo-30min")
# reCAPTCHA (v2 checkbox) keys
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")
RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET", "")

# Google Search Console HTML file verification
@app.route("/google7a446eda7ed44043.html")
def google_site_verification():
    # Must return this exact content per Google instructions
    return (
        "google-site-verification: google7a446eda7ed44043.html",
        200,
        {"Content-Type": "text/html; charset=utf-8"},
    )

# Dynamic handler for other Google verification tokens (avoids 404s for new tokens)
@app.route("/google<token>.html")
def google_site_verification_dynamic(token):
    # Allow-list tokens you verify in Search Console
    allowed = {
        "7a446eda7ed44043",
        "bec65549df0251cf",
    }
    if token in allowed:
        body = f"google-site-verification: google{token}.html"
        return body, 200, {"Content-Type": "text/html; charset=utf-8"}
    # If not in allow-list, return 404 (don’t leak existence)
    return ("Not Found", 404)

# Mock catalog for LLM and Image models
CATALOG = [
    {
        "id": "llm-pro-70b",
        "name": "LLM Pro 70B",
        "type": "llm",
        "price": 3900.0,
        "short": "Enterprise-grade 70B parameter LLM",
        "image": "https://images.unsplash.com/photo-1526498460520-4c246339dccb?w=800&q=80&auto=format&fit=crop",
        "features": [
            "State-of-the-art reasoning",
            "Fine-tuning ready",
            "Latency-optimized serving",
        ],
        "context_window": 8192,
        "params": "70B",
        "latency_ms": 120,
    },
    {
        "id": "llm-lite-7b",
        "name": "LLM Lite 7B",
        "type": "llm",
        "price": 3900.0,
        "short": "Cost-effective 7B general LLM",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80&auto=format&fit=crop",
        "features": [
            "Great for prototyping",
            "Low memory footprint",
            "Fast inference",
        ],
        "context_window": 8192,
        "params": "7B",
        "latency_ms": 95,
    },
    {
        "id": "img-gen-studio",
        "name": "ImageGen Studio",
        "type": "image",
        "price": 149.0,
        "short": "Photorealistic image generation",
        "image": "https://images.unsplash.com/photo-1542751110-97427bbecf20?w=800&q=80&auto=format&fit=crop",
        "features": [
            "Text-to-image & img2img",
            "LoRA support",
            "Hi-res fix & upscaler",
        ],
        "modes": "txt2img,img2img",
        "latency_ms": 1800,
    },
    {
        "id": "img-gen-lite",
        "name": "ImageGen Lite",
        "type": "image",
        "price": 3900.0,
        "short": "Fast, lightweight image model",
        "image": "https://images.unsplash.com/photo-1543968996-ee822b8176da?w=800&q=80&auto=format&fit=crop",
        "features": [
            "Great defaults",
            "Mobile/edge friendly",
            "Quick drafts",
        ],
        "modes": "txt2img",
        "latency_ms": 1200,
    },
    {
        "id": "model-custom",
        "name": "Create Your Own Model",
        "type": "llm",
        "price": 3900.0,
        "short": "Configure 30+ options: framework, size, latency, compliance, and more",
        "image": "https://images.unsplash.com/photo-1555255707-c07966088b7b?w=800&q=80&auto=format&fit=crop",
        "features": [
            "Frameworks: PyTorch/TF/JAX",
            "Sizes: 1B–70B+",
            "Finetuning: LoRA/QLoRA/Full",
        ],
    },
    # New additions with thumbnails
    {
        "id": "multimodal-vision-8b",
        "name": "Multimodal Vision 8B",
        "type": "multimodal",
        "price": 3900.0,
        "short": "Vision + Text reasoning with OCR",
        "image": "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?w=800&q=80&auto=format&fit=crop",
        "features": ["OCR", "Charts & tables", "Grounded captions"],
        "latency_ms": 220,
    },
    {
        "id": "code-gen-20b",
        "name": "Code Gen 20B",
        "type": "llm",
        "price": 3900.0,
        "short": "High-accuracy code generation",
        "image": "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?w=800&q=80&auto=format&fit=crop",
        "features": ["Multi-language", "Tests & docs", "Refactor mode"],
        "latency_ms": 140,
    },
    {
        "id": "speech-tts-pro",
        "name": "Speech TTS Pro",
        "type": "audio",
        "price": 3900.0,
        "short": "Neural TTS with cloning",
        "image": "https://images.unsplash.com/photo-1492724441997-5dc865305da7?w=800&q=80&auto=format&fit=crop",
        "features": ["Cloning", "Emotion", "SSML"],
    },
    {
        "id": "image-gen-pro",
        "name": "ImageGen Pro",
        "type": "image",
        "price": 3900.0,
        "short": "High-fidelity diffusion model",
        "image": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=800&q=80&auto=format&fit=crop",
        "features": ["Style control", "Upscaling", "In/Outpainting"],
    },
    {
        "id": "embedding-1",
        "name": "Embedding-1",
        "type": "tool",
        "price": 3900.0,
        "short": "Fast embeddings for RAG",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80&auto=format&fit=crop",
        "features": ["768-dim", "Fast", "Low-cost"],
    },
    {
        "id": "guard-rails",
        "name": "GuardRails",
        "type": "tool",
        "price": 3900.0,
        "short": "Safety, red-team, policy enforcement",
        "image": "https://images.unsplash.com/photo-1520975922284-8b456906c813?w=800&q=80&auto=format&fit=crop",
        "features": ["Prompt shields", "Content filters", "PII masking"],
    },
    {
        "id": "reranker-qa",
        "name": "Reranker QA",
        "type": "tool",
        "price": 3900.0,
        "short": "Improved retrieval precision",
        "image": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80&auto=format&fit=crop",
        "features": ["Cross-encoder", "Context re-scoring"],
    },
    {
        "id": "diffusion-xl",
        "name": "Diffusion XL",
        "type": "image",
        "price": 3900.0,
        "short": "Photoreal XL diffusion",
        "image": "https://images.unsplash.com/photo-1495567720989-cebdbdd97913?w=800&q=80&auto=format&fit=crop",
        "features": ["Photoreal", "Consistent faces", "Hi-res"],
    },
    {
        "id": "controlnet-suite",
        "name": "ControlNet Suite",
        "type": "image",
        "price": 3900.0,
        "short": "Pose, depth, scribble guidance",
        "image": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=800&q=80&auto=format&fit=crop",
        "features": ["Canny", "Depth", "Pose"],
    },
    {
        "id": "instruct-3b",
        "name": "Instruct 3B",
        "type": "llm",
        "price": 3900.0,
        "short": "Small, instruction-tuned",
        "image": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&q=80&auto=format&fit=crop",
        "features": ["Fast", "Cheap", "Helpful"],
    },
]


def get_product(pid):
    return next((p for p in CATALOG if p["id"] == pid), None)


def _ensure_cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]


# Simple helpers (reserved for future use)


# ---- Formatting helpers & filters ----
def human_price(value):
    try:
        n = float(value)
    except Exception:
        return str(value)
    if abs(n - int(n)) < 1e-9:
        return f"${int(n):,}"
    return f"${n:,.2f}"


def human_latency_ms(ms):
    try:
        x = float(ms)
    except Exception:
        return "n/a"
    if x >= 1000:
        return f"~{x/1000:.1f} s"
    return f"~{int(round(x))} ms"


def human_ctx(n):
    try:
        x = int(n)
    except Exception:
        return "—"
    k = int(round(x/1000))
    return f"{k}K"


def norm_params(p):
    if not p:
        return "—"
    s = str(p).upper().replace('BILLION','B').replace('MILLION','M')
    return s


app.jinja_env.filters['price'] = human_price
app.jinja_env.filters['latency'] = human_latency_ms
app.jinja_env.filters['ctx'] = human_ctx

@app.context_processor
def inject_globals():
    cart_map = session.get("cart", {})
    cart_count = sum(cart_map.values()) if isinstance(cart_map, dict) else 0
    return {"cart_count": cart_count, "DEMO_LINK": DEMO_LINK, "RECAPTCHA_SITE_KEY": RECAPTCHA_SITE_KEY}


@app.route("/")
def home():
    featured = CATALOG[:3]
    def resolve_image(p):
        if p.get("image"):
            return p["image"]
        t = (p.get("type") or "").lower()
        if t == "llm":
            return url_for('static', filename='img/models/llm.svg')
        if t == "image":
            return url_for('static', filename='img/models/image.svg')
        return url_for('static', filename='img/models/generic.svg')
    def format_label(p):
        t = (p.get("type") or "").lower()
        if t == "llm":
            return "Chat / Text"
        if t == "image":
            return "Image Gen"
        return (p.get("type") or "Model").title()
    def make_badges(p):
        t = (p.get("type") or "").lower()
        lat = p.get('latency_ms')
        if t == "llm":
            return [
                {"k":"Latency","v": human_latency_ms(lat) if lat is not None else "~120 ms"},
                {"k":"Context","v": human_ctx(p.get('context_window')) if p.get('context_window') else "8K"},
                {"k":"Params","v": norm_params(p.get('params'))},
                {"k":"Safety","v":"Shielded"},
            ]
        if t == "image":
            modes = str(p.get('modes') or 'txt2img').replace(',', ' / ')
            return [
                {"k":"Latency","v": human_latency_ms(lat) if lat is not None else "~1.8 s"},
                {"k":"Modes","v": modes},
                {"k":"Upscale","v":"×4"},
                {"k":"Safety","v":"Filters"},
            ]
        if t == "audio":
            return [
                {"k":"Latency","v": human_latency_ms(lat) if lat is not None else "~200 ms"},
                {"k":"Voices","v":"Cloning"},
                {"k":"Format","v":"MP3 / WAV"},
                {"k":"Safety","v":"PG"},
            ]
        return [
            {"k":"Latency","v": human_latency_ms(lat) if lat is not None else "n/a"},
            {"k":"Context","v":"—"},
            {"k":"Params","v": norm_params(p.get('params'))},
            {"k":"Safety","v":"—"},
        ]
    featured_with_images = [dict(p, resolved_image=resolve_image(p), format_label=format_label(p), badges=make_badges(p)) for p in featured]
    return render_template("index.html", featured=featured_with_images)


@app.route("/products")
def products():
    f = request.args.get("type")
    q = (request.args.get("q") or "").strip().lower()
    sort = request.args.get("sort")  # price_asc | price_desc | name
    # optional numeric filters
    def _to_float(x):
        try:
            return float(x)
        except Exception:
            return None
    min_price = _to_float(request.args.get("min_price"))
    max_price = _to_float(request.args.get("max_price"))
    items = [p for p in CATALOG if (p["type"] == f)] if f else list(CATALOG)
    if q:
        def matches(p):
            text = " ".join([
                p.get("name", ""),
                p.get("short", ""),
                " ".join(p.get("features", [])),
                p.get("type", ""),
                p.get("id", ""),
            ]).lower()
            return q in text
        items = [p for p in items if matches(p)]
    if min_price is not None:
        items = [p for p in items if p.get("price", 0) >= min_price]
    if max_price is not None:
        items = [p for p in items if p.get("price", 0) <= max_price]
    if sort == "price_asc":
        items = sorted(items, key=lambda p: p.get("price", 0))
    elif sort == "price_desc":
        items = sorted(items, key=lambda p: p.get("price", 0), reverse=True)
    elif sort == "name":
        items = sorted(items, key=lambda p: p.get("name", "").lower())
    # attach resolved_image for display
    def resolve_image(p):
        if p.get("image"):
            return p["image"]
        t = (p.get("type") or "").lower()
        if t == "llm":
            return url_for('static', filename='img/models/llm.svg')
        if t == "image":
            return url_for('static', filename='img/models/image.svg')
        return url_for('static', filename='img/models/generic.svg')
    def format_label(p):
        t = (p.get("type") or "").lower()
        if t == "llm":
            return "Chat / Text"
        if t == "image":
            return "Image Gen"
        return (p.get("type") or "Model").title()
    def make_badges(p):
        t = (p.get("type") or "").lower()
        lat = p.get('latency_ms')
        if t == "llm":
            return [
                {"k":"Latency","v": human_latency_ms(lat) if lat is not None else "~120 ms"},
                {"k":"Context","v": human_ctx(p.get('context_window')) if p.get('context_window') else "8K"},
                {"k":"Params","v": norm_params(p.get('params'))},
                {"k":"Safety","v":"Shielded"},
            ]
        if t == "image":
            modes = str(p.get('modes') or 'txt2img').replace(',', ' / ')
            return [
                {"k":"Latency","v": human_latency_ms(lat) if lat is not None else "~1.8 s"},
                {"k":"Modes","v": modes},
                {"k":"Upscale","v":"×4"},
                {"k":"Safety","v":"Filters"},
            ]
        if t == "audio":
            return [
                {"k":"Latency","v": human_latency_ms(lat) if lat is not None else "~200 ms"},
                {"k":"Voices","v":"Cloning"},
                {"k":"Format","v":"MP3 / WAV"},
                {"k":"Safety","v":"PG"},
            ]
        return [
            {"k":"Latency","v": human_latency_ms(lat) if lat is not None else "n/a"},
            {"k":"Context","v":"—"},
            {"k":"Params","v": norm_params(p.get('params'))},
            {"k":"Safety","v":"—"},
        ]
    items = [dict(p, resolved_image=resolve_image(p), format_label=format_label(p), badges=make_badges(p)) for p in items]
    return render_template(
        "products.html",
        products=items,
        active_filter=f,
        q=q,
        sort=sort,
        min_price=min_price,
        max_price=max_price,
    )


@app.route("/product/<pid>")
def product_detail(pid):
    p = get_product(pid)
    if not p:
        return render_template("404.html"), 404
    # add resolved image
    def resolve_image(pp):
        if pp.get("image"):
            return pp["image"]
        t = (pp.get("type") or "").lower()
        if t == "llm":
            return url_for('static', filename='img/models/llm.svg')
        if t == "image":
            return url_for('static', filename='img/models/image.svg')
        return url_for('static', filename='img/models/generic.svg')
    def format_label(pp):
        t = (pp.get("type") or "").lower()
        if t == "llm":
            return "Chat / Text"
        if t == "image":
            return "Image Gen"
        return (pp.get("type") or "Model").title()
    def make_badges(pp):
        t = (pp.get("type") or "").lower()
        if t == "llm":
            return [{"k":"Latency","v":"~120ms"},{"k":"Context","v":"8k"},{"k":"Params","v":"7B–70B"},{"k":"Safety","v":"Shielded"}]
        if t == "image":
            return [{"k":"Latency","v":"~1.8s"},{"k":"Modes","v":"txt2img/img2img"},{"k":"Upscale","v":"×4"},{"k":"Safety","v":"Filters"}]
        if t == "audio":
            return [{"k":"Latency","v":"~200ms"},{"k":"Voices","v":"Cloning"},{"k":"Format","v":"MP3/WAV"},{"k":"Safety","v":"PG"}]
        return [{"k":"Latency","v":"n/a"},{"k":"Context","v":"—"},{"k":"Params","v":"—"},{"k":"Safety","v":"—"}]
    p = dict(p, resolved_image=resolve_image(p), format_label=format_label(p), badges=make_badges(p))
    return render_template("product_detail.html", product=p)


@app.route("/cart")
def cart():
    _ensure_cart()
    cart_map = session.get("cart", {})
    items = []
    subtotal = 0.0
    for pid, qty in cart_map.items():
        p = get_product(pid)
        if p:
            # Apply dynamic pricing/name for custom model if configured
            if p["id"] == "model-custom":
                cfg = session.get("custom_model")
                if cfg:
                    p = dict(p)
                    p["price"] = cfg.get("price", p["price"]) or 0.0
                    p["name"] = cfg.get("display_name", p["name"]) or p["name"]
            total = p["price"] * qty
            subtotal += total
            items.append({"product": p, "qty": qty, "total": total})
    return render_template("cart.html", items=items, subtotal=subtotal)


@app.post("/cart/add")
def add_to_cart():
    pid = request.form.get("pid")
    qty = int(request.form.get("qty", 1))
    p = get_product(pid)
    if not p:
        return redirect(url_for("products"))
    cart_map = _ensure_cart()
    cart_map[pid] = cart_map.get(pid, 0) + max(1, qty)
    session.modified = True
    return redirect(url_for("cart"))


@app.get("/cart.json")
def cart_json():
    cart_map = session.get("cart", {})
    items = []
    subtotal = 0.0
    def resolve_image(pp):
        if pp.get("image"):
            return pp["image"]
        t = (pp.get("type") or "").lower()
        if t == "llm":
            return url_for('static', filename='img/models/llm.svg')
        if t == "image":
            return url_for('static', filename='img/models/image.svg')
        return url_for('static', filename='img/models/generic.svg')
    for pid, qty in cart_map.items():
        p = get_product(pid)
        if not p: continue
        price = p.get("price", 0.0)
        total = price * qty
        subtotal += total
        items.append({
            "id": pid,
            "name": p.get("name"),
            "price": price,
            "qty": qty,
            "image": resolve_image(p),
            "type": p.get("type"),
            "total": total,
        })
    return jsonify({"items": items, "subtotal": round(subtotal,2)})


@app.post("/cart/set")
def cart_set():
    pid = request.form.get("pid") or (request.json.get("pid") if request.is_json else None)
    qty_raw = request.form.get("qty") or (request.json.get("qty") if request.is_json else None)
    if not pid:
        return jsonify({"ok": False, "error": "pid required"}), 400
    try:
        qty = max(0, int(qty_raw))
    except Exception:
        qty = 0
    cart_map = _ensure_cart()
    if qty == 0:
        cart_map.pop(pid, None)
    else:
        cart_map[pid] = qty
    session.modified = True
    return cart_json()


@app.post("/cart/update")
def update_cart():
    cart_map = _ensure_cart()
    for pid, qty in request.form.items():
        if pid.startswith("qty_"):
            prod_id = pid.replace("qty_", "")
            try:
                q = max(0, int(qty))
            except ValueError:
                q = 0
            if q == 0:
                cart_map.pop(prod_id, None)
            else:
                cart_map[prod_id] = q
    session.modified = True
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_map = session.get("cart", {})
    if request.method == "POST":
        # Simulate a successful checkout and record an invoice for dashboard
        items = []
        subtotal = 0.0
        for pid, qty in cart_map.items():
            p = get_product(pid)
            if not p:
                continue
            line_total = p.get("price", 0.0) * qty
            subtotal += line_total
            items.append({
                "id": pid,
                "name": p.get("name"),
                "qty": qty,
                "price": p.get("price", 0.0),
                "total": line_total,
            })
        invoices = session.get("invoices", [])
        invoice_id = f"INV-{len(invoices)+1:04d}"
        invoices.append({
            "id": invoice_id,
            "amount": round(subtotal, 2),
            "currency": "USD",
            "status": "paid",
            "items": items,
        })
        session["invoices"] = invoices
        # Track purchased product ids
        owned = set(session.get("owned_models", []))
        for it in items:
            owned.add(it["id"])
        session["owned_models"] = list(owned)
        # Clear cart
        session.pop("cart", None)
        session.modified = True
        return render_template("checkout.html", success=True)
    # compute subtotal
    subtotal = 0.0
    for pid, qty in cart_map.items():
        p = get_product(pid)
        if p:
            subtotal += p["price"] * qty
    return render_template("checkout.html", success=False, subtotal=subtotal)


@app.route("/pricing")
def pricing():
    tiers = [
        {
            "id": "starter",
            "name": "Starter",
            "price": 0,
            "period": "forever",
            "features": [
                "Free API key",
                "1K requests/mo",
                "Community support",
            ],
            "cta": "Get started",
        },
        {
            "id": "pro",
            "name": "Pro",
            "price": 99,
            "period": "mo",
            "features": [
                "100K requests/mo",
                "Priority support",
                "Model customization",
            ],
            "cta": "Start Pro",
            "highlight": True,
        },
        {
            "id": "enterprise",
            "name": "Enterprise",
            "price": None,
            "period": "",
            "features": [
                "Unlimited requests",
                "SLA & dedicated SRE",
                "On-prem / VPC deploys",
            ],
            "cta": "Contact sales",
        },
    ]
    return render_template("pricing.html", tiers=tiers)

@app.route("/compare")
def compare():
    a = request.args.get("a")
    b = request.args.get("b")
    pa = get_product(a) if a else None
    pb = get_product(b) if b else None
    
    def format_label(pp):
        if not pp: return None
        t = (pp.get("type") or "").lower()
        if t == "llm":
            return "Chat / Text"
        if t == "image":
            return "Image Gen"
        return (pp.get("type") or "Model").title()
    def make_badges(pp):
        if not pp: return []
        t = (pp.get("type") or "").lower()
        if t == "llm":
            return [{"k":"Latency","v":"~120ms"},{"k":"Context","v":"8k"},{"k":"Params","v":"7B–70B"},{"k":"Safety","v":"Shielded"}]
        if t == "image":
            return [{"k":"Latency","v":"~1.8s"},{"k":"Modes","v":"txt2img/img2img"},{"k":"Upscale","v":"×4"},{"k":"Safety","v":"Filters"}]
        if t == "audio":
            return [{"k":"Latency","v":"~200ms"},{"k":"Voices","v":"Cloning"},{"k":"Format","v":"MP3/WAV"},{"k":"Safety","v":"PG"}]
        return [{"k":"Latency","v":"n/a"},{"k":"Context","v":"—"},{"k":"Params","v":"—"},{"k":"Safety","v":"—"}]
    if pa:
        pa = dict(pa, format_label=format_label(pa), badges=make_badges(pa))
    if pb:
        pb = dict(pb, format_label=format_label(pb), badges=make_badges(pb))
    # Provide options for selects
    options = [
        {"id": p["id"], "name": p["name"], "type": p["type"]}
        for p in CATALOG
    ]
    return render_template("compare.html", a=pa, b=pb, options=options)

@app.route("/testimonials")
def testimonials():
    quotes = [
        {
            "company": "Acme Corp",
            "name": "Maya Patel, CTO",
            "quote": "NovaForge models helped us cut inference costs by 38% while improving accuracy.",
        },
        {
            "company": "Shoply",
            "name": "Luis Gomez, Head of AI",
            "quote": "Integration took one afternoon. Latency dropped below 200ms across regions.",
        },
        {
            "company": "MedLink",
            "name": "Sara Chen, VP Eng",
            "quote": "Finetuning with LoRA gave us state-of-the-art clinical summarization in weeks.",
        },
    ]
    return render_template("testimonials.html", quotes=quotes)

@app.route("/faq")
def faq():
    faqs = [
        {"q": "What models do you offer?", "a": "State-of-the-art LLMs and image models with fine-tuning options."},
        {"q": "How do I get started?", "a": "Create a free account and grab your API key. Upgrade anytime."},
        {"q": "Where can I deploy?", "a": "Cloud, on‑prem, or VPC. Enterprise SLAs available."},
    ]
    return render_template("faq.html", faqs=faqs)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/dashboard")
def dashboard():
    user = session.get("user", {"name": "Guest", "email": "guest@example.com"})
    invoices = session.get("invoices", [])
    owned = session.get("owned_models", [])
    owned_set = set(owned)
    owned_products = [p for p in CATALOG if p["id"] in owned_set]
    total_models = len(CATALOG)
    purchased = len(owned)
    plan = session.get("plan", {"name": "Starter", "price": 0, "period": "forever"})
    # Recent activity from invoices
    activity = []
    for inv in reversed(invoices[-5:]):
        for it in inv.get("items", []):
            activity.append({
                "label": f"Purchased {it['qty']}× {it['name']}",
                "meta": f"${it['total']:,.2f} — {inv['id']}"
            })
    return render_template(
        "dashboard.html",
        user=user,
        stats={"total_models": total_models, "purchased": purchased, "plan": plan},
        invoices=invoices[-6:],
        activity=activity[:6],
        owned_products=owned_products,
    )


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        data = request.form if request.form else (request.json or {})
        user = session.get("user", {})
        user["name"] = data.get("name", user.get("name", ""))
        user["email"] = data.get("email", user.get("email", ""))
        session["user"] = user
        session["newsletter"] = True if str(data.get("newsletter", "")).lower() in ("true", "1", "on") else False
        if data.get("regen_key"):
            session["api_key"] = f"sk-{os.urandom(6).hex()}-{os.urandom(4).hex()}"
        session.modified = True
        return redirect(url_for("settings"))
    # GET
    user = session.get("user", {"name": "Guest", "email": "guest@example.com"})
    api_key = session.get("api_key") or f"sk-{os.urandom(6).hex()}-{os.urandom(4).hex()}"
    session.setdefault("api_key", api_key)
    newsletter = bool(session.get("newsletter", False))
    plan = session.get("plan", {"name": "Starter", "price": 0, "period": "forever"})
    return render_template("settings.html", user=user, api_key=api_key, newsletter=newsletter, plan=plan)


@app.route("/industry/<slug>")
def industry(slug):
    data = INDUSTRIES.get(slug)
    if not data:
        return render_template("404.html"), 404
    # attach recommended models by simple heuristic
    recs = []
    if slug == "finance":
        recs = [p for p in CATALOG if p.get("type") in ("llm", "multimodal")][:3]
    elif slug == "manufacturing" or slug == "logistics":
        recs = [p for p in CATALOG if p.get("type") in ("llm", "image")][:3]
    elif slug == "retail":
        recs = [p for p in CATALOG if p.get("type") in ("llm", "image")][:3]
    elif slug == "healthcare":
        recs = [p for p in CATALOG if p.get("type") in ("llm", "multimodal")][:3]
    # resolve images and labels
    def resolve_image(p):
        if p.get("image"):
            return p["image"]
        t = (p.get("type") or "").lower()
        if t == "llm":
            return url_for('static', filename='img/models/llm.svg')
        if t == "image":
            return url_for('static', filename='img/models/image.svg')
        return url_for('static', filename='img/models/generic.svg')
    def format_label(p):
        t = (p.get("type") or "").lower()
        if t == "llm": return "Chat / Text"
        if t == "image": return "Image Gen"
        return (p.get("type") or "Model").title()
    recs = [dict(p, resolved_image=resolve_image(p), format_label=format_label(p)) for p in recs]
    return render_template("industry_detail.html", industry=data, slug=slug, recs=recs)

@app.route("/models/create", methods=["GET", "POST"]) 
def create_model():
    if request.method == "POST":
        f = request.form
        action = f.get("action", "add_to_cart")
        framework = f.get("framework", "PyTorch")
        size = f.get("size", "7B")
        modality = f.get("modality", "text")
        context = int(f.get("context", 4096))
        quant = f.get("quantization", "FP16")
        finetune = f.get("finetune", "LoRA")
        rlhf = bool(f.get("rlhf"))
        safety = bool(f.get("safety"))
        retrieval = bool(f.get("retrieval"))
        vectordb = f.get("vectordb", "faiss")
        tokenizer = f.get("tokenizer", "bpe")
        multilingual = bool(f.get("multilingual"))
        streaming = bool(f.get("streaming"))
        function_calling = bool(f.get("function_calling"))
        tools = bool(f.get("tools"))
        batch_size = int(f.get("batch_size", 8))
        latency_ms = int(f.get("latency", 300))
        throughput_rps = int(f.get("throughput", 50))
        gpu = f.get("gpu", "A100")
        regions = f.getlist("regions") or ["us-east"]
        compliance = f.getlist("compliance")
        logging = bool(f.get("logging"))
        monitoring = bool(f.get("monitoring"))
        autoscale = bool(f.get("autoscale"))
        endpoints = f.getlist("endpoints")
        auth = f.get("auth", "token")
        sdks = f.getlist("sdks")
        sla = f.get("sla", "standard")
        budget = f.get("budget", "standard")
        project_name = f.get("project_name", "My Custom Model")
        use_case = f.get("use_case", "")
        notes = f.get("notes", "")
        scrape_text = f.getlist("scrape_text")
        scrape_image = f.getlist("scrape_image")

        # Price model: premium base + large increments for advanced features
        price = 70000.0
        size_map = {"1B": 0, "7B": 20000, "13B": 40000, "34B": 90000, "70B": 180000}
        price += size_map.get(size, 0)
        if context > 4096:
            price += (context - 4096) / 1024 * 500  # +$500 per extra 1k tokens
        if quant in ("FP16", "FP32"):
            price += 1000
        if finetune in ("Full",):
            price += 30000
        if finetune in ("LoRA", "QLoRA"):
            price += 12000
        if rlhf:
            price += 25000
        if retrieval:
            price += 12000
        if multilingual:
            price += 9000
        if streaming:
            price += 4000
        if function_calling:
            price += 6000
        if tools:
            price += 4000
        if latency_ms < 150:
            price += 20000
        if throughput_rps > 100:
            price += 15000
        if gpu in ("H100",):
            price += 18000
        price += 8000 * len(regions)
        price += 10000 * len(compliance)
        if autoscale:
            price += 6000
        price += 3000 * len(endpoints)
        price += 3000 * len(sdks)
        # Data sourcing costs
        price += 8000 * len(scrape_text)
        price += 5000 * len(scrape_image)
        if sla == "premium":
            price += 12000
        if budget == "enterprise":
            price += 25000

        # Build time estimate (days): premium baseline + strong increments
        days = 45
        size_days = {"1B": 0, "7B": 10, "13B": 20, "34B": 30, "70B": 40}
        days += size_days.get(size, 0)
        if context > 4096:
            days += int((context - 4096) / 4096) * 5
        if finetune == "Full":
            days += 25
        elif finetune in ("LoRA", "QLoRA"):
            days += 12
        if rlhf:
            days += 20
        if retrieval:
            days += 10
        if multilingual:
            days += 8
        if streaming:
            days += 4
        if function_calling:
            days += 6
        if tools:
            days += 5
        if latency_ms < 150:
            days += 10
        if throughput_rps > 100:
            days += 8
        if gpu == "H100":
            days += 5
        days += 7 * len(regions)
        days += 10 * len(compliance)
        if autoscale:
            days += 7
        days += 4 * len(endpoints)
        days += 3 * len(sdks)

        display_name = f"Custom Model ({framework}, {size})"
        cfg = {
            "framework": framework,
            "size": size,
            "modality": modality,
            "context": context,
            "quantization": quant,
            "finetune": finetune,
            "rlhf": rlhf,
            "safety": safety,
            "retrieval": retrieval,
            "vectordb": vectordb,
            "tokenizer": tokenizer,
            "multilingual": multilingual,
            "streaming": streaming,
            "function_calling": function_calling,
            "tools": tools,
            "batch_size": batch_size,
            "latency_ms": latency_ms,
            "throughput_rps": throughput_rps,
            "gpu": gpu,
            "regions": regions,
            "compliance": compliance,
            "logging": logging,
            "monitoring": monitoring,
            "autoscale": autoscale,
            "endpoints": endpoints,
            "auth": auth,
            "sdks": sdks,
            "sla": sla,
            "budget": budget,
            "scrape_text": scrape_text,
            "scrape_image": scrape_image,
            "project_name": project_name,
            "use_case": use_case,
            "notes": notes,
            "price": round(price, 2),
            "display_name": display_name,
            "build_days": int(days),
        }
        # compute build time estimate (days)
        def _estimate_days():
            base = 5
            size_days = {"1B": 1, "7B": 3, "13B": 5, "34B": 9, "70B": 14}
            d = base + size_days.get(size, 6)
            if finetune == "Full":
                d += 6
            elif finetune in ("LoRA", "QLoRA"):
                d += 3
            if rlhf:
                d += 5
            if retrieval:
                d += 2
            if multilingual:
                d += 2
            if function_calling or tools:
                d += 1
            d += max(0, (context - 4096) // 4096)
            d += len(regions)
            d += len(compliance)
            if sla == "premium":
                d += 1
            return max(3, d)

        cfg["build_days"] = _estimate_days()
        session["custom_model"] = cfg
        session.modified = True

        if action == "generate":
            return redirect(url_for("create_model_result"))
        else:
            cart_map = _ensure_cart()
            cart_map["model-custom"] = 1
            session.modified = True
            return redirect(url_for("cart"))

    options = {
        "frameworks": ["PyTorch", "TensorFlow", "JAX"],
        "sizes": ["1B", "7B", "13B", "34B", "70B"],
        "modalities": ["text", "image", "multimodal"],
        "contexts": [2048, 4096, 8192, 16384, 32768],
        "quantizations": ["INT4", "INT8", "FP16", "FP32"],
        "finetunes": ["LoRA", "QLoRA", "Full"],
        "vectordbs": ["faiss", "milvus", "pgvector", "elasticsearch"],
        "tokenizers": ["bpe", "sentencepiece"],
        "gpus": ["A100", "H100", "L40S"],
        "regions": ["us-east", "us-west", "eu-west", "ap-south", "ap-northeast"],
        "compliance": ["GDPR", "HIPAA", "SOC2", "ISO27001"],
        "endpoints": ["/v1/chat", "/v1/embeddings", "/v1/completions"],
        "auth": ["token", "oauth2", "mTLS"],
        "sdks": ["python", "javascript", "go", "java"],
        "sla": ["standard", "premium"],
        "budget": ["startup", "standard", "enterprise"],
        "scrape_text": ["wikipedia", "arxiv", "commoncrawl", "pubmed", "stackexchange", "github"],
        "scrape_image": ["pixabay", "duckduckgo", "unsplash", "pexels", "custom_s3"],
    }
    return render_template("create_model.html", options=options)


@app.route("/models/result")
def create_model_result():
    cfg = session.get("custom_model")
    if not cfg:
        return redirect(url_for("create_model"))
    return render_template("create_model_result.html", cfg=cfg)


@app.post("/models/add_current_to_cart")
def add_current_custom_to_cart():
    cfg = session.get("custom_model")
    if not cfg:
        return redirect(url_for("create_model"))
    cart_map = _ensure_cart()
    cart_map["model-custom"] = 1
    session.modified = True
    return redirect(url_for("cart"))


@app.route("/login")
def login():
    return render_template("auth_login.html")


@app.route("/register")
def register():
    return render_template("auth_register.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Collect form fields
        data = {
            "name": (request.form.get("name") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "company": (request.form.get("company") or "").strip(),
            "phone": (request.form.get("phone") or "").strip(),
            "subject": (request.form.get("subject") or "").strip(),
            "category": (request.form.get("category") or "").strip() or "Other",
            "budget": (request.form.get("budget") or "").strip() or "Undisclosed",
            "message": (request.form.get("message") or "").strip(),
            "consent": request.form.get("consent") == "on",
        }
        # Basic validation
        error = None
        if not data["name"] or not data["email"] or not data["subject"] or not data["message"]:
            error = "Please fill in your name, email, subject, and message."
        elif not data["consent"]:
            error = "Please accept the contact consent to proceed."
        # reCAPTCHA validation (if configured)
        if not error and RECAPTCHA_SECRET:
            token = request.form.get('g-recaptcha-response', '')
            if not token:
                error = "Please complete the reCAPTCHA."
            else:
                try:
                    params = urllib.parse.urlencode({
                        'secret': RECAPTCHA_SECRET,
                        'response': token,
                        'remoteip': request.remote_addr or ''
                    }).encode()
                    req = urllib.request.Request('https://www.google.com/recaptcha/api/siteverify', data=params)
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        res = json.loads(resp.read().decode('utf-8'))
                    if not res.get('success'):
                        error = "reCAPTCHA verification failed. Please try again."
                except Exception:
                    error = "Could not verify reCAPTCHA. Please try again."
        if error:
            return render_template("contact.html", submitted=False, error=error, data=data)

        # In production: route by category (e.g., send email or webhook)
        # Example:
        # if data["category"].lower() == "sales": send_to_sales(data)
        # elif data["category"].lower() == "support": send_to_support(data)
        return render_template("contact.html", submitted=True, data=data)
    return render_template("contact.html", submitted=False, data=None)


@app.route("/support")
def support():
    return render_template("support.html")


@app.get("/status.json")
def status_json():
    # In production, compute status from health checks (DB, API keys, queue, etc.)
    return jsonify({
        "ok": True,
        "status": "operational",
        "uptime": "99.99%",
        "regions": ["US", "EU"],
        "updated": True
    })


# Simple Model Playground
@app.route("/playground")
def playground():
    models = [{"id": p["id"], "name": p["name"], "type": p.get("type")} for p in CATALOG if p.get("id") != "model-custom"]
    return render_template("playground.html", models=models)


@app.post("/api/playground")
def api_playground():
    data = request.get_json(silent=True) or {}
    pid = (data.get("model") or "").strip()
    prompt = (data.get("prompt") or "").strip()
    p = get_product(pid)
    if not p:
        return jsonify({"ok": False, "error": "Unknown model"}), 400
    t = (p.get("type") or "").lower()
    if t == "image":
        # return an example image URL using the prompt as a seed (unsplash dynamic query)
        q = urllib.parse.quote_plus(prompt or p.get('name') or 'image')
        img = f"https://source.unsplash.com/featured/1024x576?{q}"
        return jsonify({"ok": True, "type": "image", "image": img, "model": pid})
    # default: llm-like text
    base = prompt or "Explain how this model helps my use case."
    text = (
        f"{p.get('name')} says:\n" 
        f"• {base}\n" 
        f"• Key strengths: latency {human_latency_ms(p.get('latency_ms'))}, context {human_ctx(p.get('context_window') or 8000)}\n"
        f"• Getting started: use the Templates on the model page or our SDK."
    )
    return jsonify({"ok": True, "type": "text", "text": text, "model": pid})

# Industry long-form content (trimmed for brevity; expand in production)
INDUSTRIES = {
    "finance": {
        "title": "Finance",
        "summary": "LLMs transform research, compliance, fraud triage, and customer experience across banking, markets, and fintech.",
        "sections": [
            {
                "heading": "Executive Overview",
                "content": (
                    "From front-office advisory to middle-office risk and back-office operations, LLMs compress knowledge work cycles. "
                    "They surface insights from filings and market data, explain transactions to customers, and accelerate KYC/AML."
                ),
            },
            {
                "heading": "Key Use Cases",
                "bullets": [
                    "Analyst co-pilot for earnings summarization and comparable analysis",
                    "Fraud alert triage with natural-language explanations",
                    "Automated KYC document extraction and validation",
                    "Regulatory change tracking with impact summaries",
                ],
            },
            {
                "heading": "Implementation Patterns",
                "content": (
                    "Blend retrieval-augmented generation (RAG) on curated corpora with fine-tuned models for institutional tone. "
                    "Adopt human-in-the-loop review for material decisions; log prompts and outputs for auditability."
                ),
            },
        ],
        "charts": {
            "adoption": {
                "labels": ["Research", "Fraud", "KYC", "Support"],
                "data": [78, 64, 72, 81],
                "title": "AI Adoption by Function (%)",
            },
            "roi": {
                "labels": ["Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"],
                "data": [1.2, 1.6, 2.1, 2.8],
                "title": "Modeled ROI Multiplier Over First Year",
            },
        },
    },
    "healthcare": {
        "title": "Healthcare",
        "summary": "Clinical summarization, coding assistance, patient triage, and prior auth drafting with safety controls.",
        "sections": [
            {"heading": "Executive Overview", "content": "LLMs reduce clerical burden and improve patient communication with audit trails and PHI safeguards."},
            {"heading": "Key Use Cases", "bullets": ["Note summarization", "ICD/CPT suggestions", "Triage chat", "Discharge instruction drafting"]},
        ],
        "charts": {
            "adoption": {"labels": ["Clinics", "Hospitals", "Payers"], "data": [55, 62, 47], "title": "Adoption by Segment (%)"}
        },
    },
    "ecommerce": {
        "title": "E‑commerce",
        "summary": "Catalog scale-up, conversational shopping, and returns analysis with multilingual coverage.",
        "sections": [
            {"heading": "Executive Overview", "content": "LLMs personalize discovery and reduce support load, improving conversion and AOV."},
            {"heading": "Key Use Cases", "bullets": ["Descriptions", "Assistants", "Review insights", "Return triage"]},
        ],
        "charts": {
            "roi": {"labels": ["Q1", "Q2", "Q3", "Q4"], "data": [1.1, 1.4, 1.9, 2.3], "title": "Projected ROI"}
        },
    },
    "education": {
        "title": "Education",
        "summary": (
            "Large Language Models are transforming education by acting as tutors, assistants, content creators, and personalized "
            "learning companions. They adapt to each learner’s pace, provide instant feedback, and make education more interactive, "
            "inclusive, and scalable."
        ),
        "art": True,
        "sections": [
            {"heading": "1. Personalized Learning", "bullets": [
                "Adaptive Study Plans: Custom learning paths based on strengths, weaknesses, and pace.",
                "Skill-Level Adjustments: Exercises adapt dynamically to performance.",
                "Goal Tracking: Progress monitoring and daily objective adjustment."
            ]},
            {"heading": "2. Intelligent Tutoring Systems", "bullets": [
                "On-Demand Q&A: Instant answers with multi-explanation styles.",
                "Step-by-Step Problem Solving: Break down math/science/language problems.",
                "Exam Preparation: Personalized practice questions with hints."
            ]},
            {"heading": "3. Content Creation & Enhancement", "bullets": [
                "Lesson Plan Generation: Curriculum-aligned outlines in minutes.",
                "Custom Worksheets & Quizzes: Auto-generated exercises and assessments.",
                "Interactive Materials: Stories, simulations, and case studies."
            ]},
            {"heading": "4. Language Learning Support", "bullets": [
                "Conversational Practice: Virtual speaking partner across languages.",
                "Grammar & Vocabulary Guidance: Corrections with explanations.",
                "Cultural Context: Language taught alongside cultural nuances."
            ]},
            {"heading": "5. Writing Assistance", "bullets": [
                "Essay Feedback: Grammar, structure, and argument quality.",
                "Paraphrasing & Plagiarism Checks: Preserve originality and clarity.",
                "Creative Coaching: Plot twists, character arcs, and themes."
            ]},
            {"heading": "6. Research Assistance", "bullets": [
                "Summarizing Articles: Concise overviews of long academic texts.",
                "Reference Suggestions: Credible sources and citations.",
                "Data Interpretation: Explain charts, statistics, and findings."
            ]},
            {"heading": "7. Accessibility in Education", "bullets": [
                "Text-to-Speech & Speech-to-Text: Support diverse learning needs.",
                "Simplified Reading: Age-appropriate rephrasing of complex text.",
                "Sign Language Integration: Descriptions aligned to lessons."
            ]},
            {"heading": "8. Teacher Productivity Tools", "bullets": [
                "Automated Grading: Scores with individualized feedback.",
                "Administrative Automation: Draft emails, reports, and communications.",
                "Curriculum Mapping: Align lessons to standards."
            ]},
            {"heading": "9. Gamified Learning", "bullets": [
                "Adaptive Educational Games: Difficulty scales with performance.",
                "Story-Based Learning: Narrative-driven curricula.",
                "Leaderboards & Achievements: Motivation via progress tracking."
            ]},
            {"heading": "10. Collaboration & Group Learning", "bullets": [
                "Project Assistance: Roles, timelines, and resources suggestions.",
                "Peer Feedback Guidance: Constructive critique scaffolding.",
                "Debate Moderation: Structured discourse and argumentation."
            ]},
            {"heading": "11. Lifelong Learning & Professional Training", "bullets": [
                "Career Skills: Micro-courses tailored to industry needs.",
                "Certification Prep: Practice questions and timed mocks.",
                "Corporate Training: Personalized training modules."
            ]},
            {"heading": "12. Future Possibilities", "bullets": [
                "AI-Powered Classrooms: LLMs as co-teachers in hybrid/remote settings.",
                "Global Access: Translation and localization of entire curricula.",
                "Immersive Worlds: VR + LLM tutors in simulated environments."
            ]}
        ],
        "charts": {
            "adoption": {
                "labels": ["K-12", "Higher Ed", "Tutoring", "Admin", "Accessibility"],
                "data": [58, 64, 71, 52, 60],
                "title": "LLM Adoption by Domain (%)",
                "type": "bar"
            },
            "outcomes": {
                "labels": ["M1", "M2", "M3", "M4", "M5", "M6"],
                "data": [1.5, 2.3, 3.0, 3.6, 4.2, 5.1],
                "title": "Learning Outcome Improvement (%)",
                "type": "line"
            },
            "maturity": {
                "labels": ["Content Gen", "Tutoring", "Assessment", "Gov", "Safety"],
                "data": [62, 55, 50, 48, 53],
                "title": "Implementation Maturity",
                "type": "radar"
            },
            "accessibility": {
                "labels": ["TTS", "STT", "Simplified Reading", "Alt Formats"],
                "data": [68, 57, 61, 49],
                "title": "Accessibility Feature Adoption (%)",
                "type": "bar"
            }
        }
    },
    "media": {
        "title": "Media",
        "summary": (
            "LLMs accelerate newsrooms and studios: drafting stories, localizing content, powering personalization, and augmenting "
            "audio/video pipelines while assisting research, moderation, and live event coverage."
        ),
        "art": True,
        "art_theme": "media",
        "sections": [
            {"heading": "1. News & Journalism", "bullets": [
                "Automated News Writing: Drafts from raw data (scores, financials, elections).",
                "Real-Time Summarization: Condense pressers, reports, and interviews.",
                "Fact-Checking Assistance: Cross-reference claims with trusted sources.",
                "Multilingual Publishing: Translate stories for global distribution."
            ]},
            {"heading": "2. Script & Story Writing", "bullets": [
                "Film & TV Scripts: Dialogue, plot arcs, and character development.",
                "Interactive Storytelling: Branching narratives for games/immersive media.",
                "Idea Brainstorming: Premises, themes, and creative twists."
            ]},
            {"heading": "3. Content Personalization", "bullets": [
                "Custom News Feeds: Tailored articles, podcasts, or videos.",
                "Adaptive Story Formats: Text article, short video script, or infographic.",
                "Recommendation Engines: Related content to sustain engagement."
            ]},
            {"heading": "4. Marketing & Promotion", "bullets": [
                "Ad Copy Generation: Headlines, slogans, and campaign messages.",
                "Social Media Posts: Platform-specific captions, threads, or reel scripts.",
                "Trend Monitoring: Track hashtags, topics, and sentiment."
            ]},
            {"heading": "5. Research & Editorial Support", "bullets": [
                "Topic Deep Dives: Summarize background for investigations.",
                "Audience Analysis: Process engagement to guide editorial decisions.",
                "Competitive Monitoring: Track coverage patterns of rivals."
            ]},
            {"heading": "6. Audio & Video Production", "bullets": [
                "Podcast Scripts: Structured outlines and talking points.",
                "Video Voiceovers: Pair LLM scripts with synthetic voice.",
                "Subtitles & Captions: Transcribe and translate A/V content."
            ]},
            {"heading": "7. Creative Assistance", "bullets": [
                "Headline Variations: Multiple options to optimize CTR.",
                "Metaphor & Analogy Creation: Enrich storytelling.",
                "Mood-Based Writing: Tone control from formal to humorous."
            ]},
            {"heading": "8. Archiving & Metadata", "bullets": [
                "Automated Tagging: Classify photos, videos, and articles.",
                "Content Summaries: Searchable abstracts for archives.",
                "Media Retrieval: Natural-language search across libraries."
            ]},
            {"heading": "9. Audience Interaction", "bullets": [
                "Conversational News Bots: Chat with stories for clarifications.",
                "Live Event Coverage: Real-time commentary for sports/awards/politics.",
                "Feedback Analysis: Summarize and categorize comments."
            ]},
            {"heading": "10. Crisis & Breaking News Management", "bullets": [
                "Fast Turnaround Coverage: Verified short updates in emergencies.",
                "Rumor Control: Detect misinformation and prepare counter-content.",
                "Live Dashboard Writing: Summaries for TV tickers/news apps."
            ]},
            {"heading": "11. Training & Internal Use", "bullets": [
                "Journalist Support Tools: Real-time grammar/style suggestions.",
                "Media Law Guidance: Flag defamation/copyright risks.",
                "Interview Prep: Background questions and fact sheets."
            ]},
            {"heading": "12. Future Possibilities", "bullets": [
                "AI-Powered Newsrooms: Automated research, writing, and editing with oversight.",
                "Immersive AI Anchors: Avatars delivering personalized video news.",
                "Audience-Driven Narratives: Viewers influence real-time stories."
            ]}
        ],
        "charts": {
            "content_mix": {
                "labels": ["News", "Opinion", "Video", "Podcast", "Social"],
                "data": [40, 15, 22, 10, 13],
                "title": "Content Mix Composition (%)",
                "type": "bar"
            },
            "engagement_growth": {
                "labels": ["W1", "W2", "W3", "W4", "W5", "W6"],
                "data": [2.1, 3.0, 4.8, 6.2, 7.0, 8.5],
                "title": "Engagement Growth (WoW %)",
                "type": "line"
            },
            "maturity": {
                "labels": ["Personalization", "A/V", "Editorial", "Safety", "Ops"],
                "data": [58, 62, 55, 50, 53],
                "title": "Implementation Maturity",
                "type": "radar"
            }
        }
    },
    "robotics": {
        "title": "Robotics",
        "summary": (
            "LLMs enable natural language interfaces, adaptive planning, and human-aware collaboration across industrial, service, "
            "healthcare, and exploratory robotics."),
        "art": True,
        "art_theme": "robotics",
        "sections": [
            {"heading": "1. Natural Language Command Processing", "bullets": [
                "Voice & Text Instructions: Interpret commands like ‘Bring me the red mug from the kitchen’.",
                "Multi-Step Task Understanding: Break down complex tasks into smaller actions.",
                "Ambiguity Resolution: Ask clarifying questions when instructions are unclear."
            ]},
            {"heading": "2. Human-Robot Interaction", "bullets": [
                "Conversational Interfaces: Communicate like a human teammate.",
                "Context Retention: Remember past interactions for consistency.",
                "Emotionally Aware Dialogue: Adjust tone based on mood or urgency."
            ]},
            {"heading": "3. Task Planning & Coordination", "bullets": [
                "Dynamic Workflow Generation: Step-by-step plans from high-level goals.",
                "Multi-Robot Coordination: Assign tasks among several robots efficiently.",
                "Adaptive Planning: Modify sequences when obstacles arise."
            ]},
            {"heading": "4. Sensor Data Interpretation", "bullets": [
                "Multi-Modal Understanding: Fuse camera, LiDAR, tactile data with LLM reasoning.",
                "Natural Language Reports: Summarize sensor readings in plain language.",
                "Anomaly Detection: Spot unusual patterns and suggest corrections."
            ]},
            {"heading": "5. Training & Programming Support", "bullets": [
                "Code Generation for Control Systems: Draft or modify control scripts.",
                "Simulation-Based Learning: Train in virtual environments with feedback.",
                "On-the-Fly Skill Teaching: Learn tasks from natural language demos."
            ]},
            {"heading": "6. Industrial & Manufacturing Robotics", "bullets": [
                "Automated Troubleshooting: Diagnose assembly faults and suggest repairs.",
                "Workflow Optimization: Improve throughput and reduce downtime.",
                "Maintenance Scheduling: Predictive/preventive maintenance via ops data."
            ]},
            {"heading": "7. Service & Hospitality Robots", "bullets": [
                "Customer Assistance: Answer questions, take orders, provide directions.",
                "Personalized Interaction: Recognize frequent users and tailor responses.",
                "Multi-Language Support: Communicate fluently with international guests."
            ]},
            {"heading": "8. Healthcare & Assistive Robotics", "bullets": [
                "Patient Support: Medication reminders and guided exercises.",
                "Elderly Assistance: Companionship and help with routines.",
                "Medical Data Communication: Explain instructions in plain language."
            ]},
            {"heading": "9. Autonomous Vehicles & Drones", "bullets": [
                "Mission Planning: Define/adjust routes in real time.",
                "Flight/Drive Report Summarization: Convert telemetry into updates.",
                "Multi-Agent Coordination: Coordinate swarms or delivery robots."
            ]},
            {"heading": "10. Research & Exploration Robotics", "bullets": [
                "Field Data Analysis: Summarize findings from exploration missions.",
                "Remote Operation Assistance: Aid operators in hazardous environments.",
                "Autonomous Hypothesis Testing: Suggest next experimental steps."
            ]},
            {"heading": "11. Safety & Compliance", "bullets": [
                "Risk Assessment: Predict hazards and mitigations.",
                "Regulatory Compliance Checks: Ensure actions follow standards.",
                "Incident Reporting: Auto-generate detailed logs after incidents."
            ]},
            {"heading": "12. Future Possibilities", "bullets": [
                "Fully Conversational Robot Operators: Reason through complex instructions via conversation.",
                "Self-Learning Robots: Autonomously acquire and refine skills.",
                "Human-AI-Robot Teams: Shared decision-making for high-stakes missions."
            ]}
        ],
        "charts": {
            "command_success": {
                "labels": ["Pick", "Place", "Navigate", "Inspect", "Assemble"],
                "data": [88, 85, 92, 81, 74],
                "title": "Command Success Rate by Task (%)",
                "type": "bar"
            },
            "throughput": {
                "labels": ["W1", "W2", "W3", "W4", "W5", "W6"],
                "data": [100, 112, 118, 130, 141, 155],
                "title": "Cell Throughput Index (baseline=100)",
                "type": "line"
            },
            "maturity": {
                "labels": ["HRI", "Planning", "Perception", "Safety", "Ops"],
                "data": [56, 60, 63, 52, 58],
                "title": "Implementation Maturity",
                "type": "radar"
            }
        }
    },
    "govtech": {
        "title": "GovTech",
        "summary": (
            "LLMs act as intelligent public service assistants, policy analysis tools, and administrative process optimizers. "
            "They help handle citizen requests, automate repetitive work, and interpret complex data to improve transparency, "
            "responsiveness, and efficiency in governance."),
        "art": True,
        "art_theme": "govtech",
        "sections": [
            {"heading": "Extensive Uses of LLMs in GovTech", "content": (
                "Large Language Models can act as intelligent public service assistants, policy analysis tools, and administrative "
                "process optimizers for governments. They can handle citizen requests in natural language, automate repetitive tasks, "
                "and help decision-makers interpret complex data — making governance more transparent, responsive, and efficient.")},
            {"heading": "1. Citizen Services & Engagement", "bullets": [
                "Virtual Government Assistants: Natural-language answers for licenses, taxes, benefits, regulations.",
                "24/7 Multilingual Support: Web, phone, and chat in preferred languages.",
                "Simplified Government Forms: Guided, step-by-step applications.",
                "Proactive Notifications: Renewals, payments, eligibility reminders."
            ]},
            {"heading": "2. Policy Research & Drafting", "bullets": [
                "Policy Summarization: Condense lengthy bills and statutes.",
                "Comparative Analysis: Cross-region/country policy comparison.",
                "Impact Forecasting: Model demographic/economic/environmental effects.",
                "Public Feedback Processing: Analyze and cluster citizen comments."
            ]},
            {"heading": "3. Administrative Automation", "bullets": [
                "Document Processing: Extract/verify/file data from forms and scans.",
                "Automated Report Generation: Instant compliance and performance reports.",
                "Workflow Optimization: Recommend steps to reduce red tape."
            ]},
            {"heading": "4. Data Transparency & Accessibility", "bullets": [
                "Open Data Summarization: Translate datasets into digestible insights.",
                "Interactive Q&A Portals: Plain-language queries over public records.",
                "Performance Dashboards: Auto-updated metrics with narrative explanations."
            ]},
            {"heading": "5. Public Safety & Crisis Response", "bullets": [
                "Emergency Communication: Clear, multilingual alerts during crises.",
                "Misinformation Detection: Flag and counter false narratives.",
                "Incident Analysis: Summarize and categorize field reports."
            ]},
            {"heading": "6. Legal & Compliance Assistance", "bullets": [
                "Regulation Interpretation: Explain legal codes in plain language.",
                "Contract Review: Detect risky or non-compliant clauses.",
                "Compliance Monitoring: Scan activities for potential violations."
            ]},
            {"heading": "7. Smart City Management", "bullets": [
                "IoT Data Interpretation: Summarize traffic, environment, grid trends.",
                "Public Service Coordination: Cross-departmental planning and handoffs.",
                "Resource Allocation: Recommend budget/staff/equipment distribution."
            ]},
            {"heading": "8. Education & Public Awareness", "bullets": [
                "Civic Education Tools: Explain structure, voting, and rights.",
                "Public Consultation Engagement: Interactive policy discussions.",
                "Training Civil Servants: On-demand learning for rules and best practices."
            ]},
            {"heading": "9. Procurement & Vendor Management", "bullets": [
                "Bid Evaluation Assistance: Summaries and highlights for reviewers.",
                "Market Intelligence: Scan news for suppliers and innovations.",
                "Fraud Detection: Spot suspicious procurement patterns."
            ]},
            {"heading": "10. Future Possibilities", "bullets": [
                "Conversational Government Portals: AI chat-driven citizen services.",
                "Policy Simulation Platforms: Model effects prior to passage.",
                "AI-Led Participatory Governance: Co-create policies with citizens."
            ]}
        ],
        "charts": {
            "service_response_time": {
                "labels": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
                "data": [18, 16, 14, 12, 11, 12, 13, 15],
                "title": "Avg. Citizen Query Response Time (mins)",
                "type": "line"
            },
            "adoption_by_department": {
                "labels": ["Tax", "Licensing", "Benefits", "Public Safety", "Transit", "Parks"],
                "data": [68, 55, 62, 47, 51, 45],
                "title": "LLM Adoption by Department (%)",
                "type": "bar"
            },
            "maturity": {
                "labels": ["CitizenSvc", "Policy", "Ops", "Data", "Safety"],
                "data": [60, 58, 55, 52, 50],
                "title": "Implementation Maturity",
                "type": "radar"
            }
        }
    },
    "legal": {
        "title": "Legal",
        "summary": (
            "LLMs serve as powerful research assistants, contract analyzers, and client communication tools. They process vast legal text, "
            "generate summaries, detect risks, and help non‑lawyers understand complex matters in plain language — improving efficiency and reducing costs."),
        "art": True,
        "art_theme": "legal",
        "sections": [
            {"heading": "Extensive Uses of LLMs in the Legal Sector", "content": (
                "Large Language Models can serve as powerful research assistants, contract analyzers, and client communication tools for legal professionals. "
                "They can process vast amounts of legal text, generate summaries, detect risks, and even help non‑lawyers understand complex legal matters in plain language — all while improving efficiency and reducing costs.")},
            {"heading": "1. Legal Research & Case Analysis", "bullets": [
                "Rapid Case Law Search: Retrieve relevant precedents from natural language queries.",
                "Judgment Summarization: Condense lengthy court decisions into key points.",
                "Comparative Legal Analysis: Compare statutes/regulations/cases across jurisdictions.",
                "Trend Analysis: Identify patterns in outcomes for litigation strategy."
            ]},
            {"heading": "2. Contract Drafting & Review", "bullets": [
                "Clause Suggestion: Recommend standard clauses by type and jurisdiction.",
                "Risk Detection: Flag vague, high‑liability, or non‑compliant terms.",
                "Version Comparison: Highlight differences between drafts.",
                "Plain Language Translation: Client‑friendly summaries of complex terms."
            ]},
            {"heading": "3. Compliance & Regulatory Monitoring", "bullets": [
                "Real‑Time Law Updates: Monitor legislative and regulatory changes.",
                "Policy Alignment Checks: Ensure internal policies meet requirements.",
                "Industry‑Specific Compliance: Tailored alerts for finance, healthcare, energy."
            ]},
            {"heading": "4. Litigation Support", "bullets": [
                "Pleadings Drafting: First drafts of complaints, motions, affidavits.",
                "Evidence Summarization: Organize and summarize discovery at scale.",
                "Deposition Preparation: Suggest questions and potential objections."
            ]},
            {"heading": "5. Client Communication", "bullets": [
                "Automated Case Updates: Plain‑language progress updates for clients.",
                "FAQ Handling: Answer common legal questions via chatbots.",
                "Document Explanation: Walk through terms and obligations."
            ]},
            {"heading": "6. Court & Judicial Assistance", "bullets": [
                "Legal Brief Summarization: Condense submissions for faster review.",
                "Precedent Matching: Suggest judgments relevant to current matters.",
                "Docket Management: Summarize case timelines and milestones."
            ]},
            {"heading": "7. Alternative Dispute Resolution", "bullets": [
                "Case Evaluation: Summarize both positions for mediators.",
                "Settlement Proposal Drafting: Suggest terms based on precedent and data.",
                "Risk Assessment: Predict outcomes to guide negotiation."
            ]},
            {"heading": "8. Public Legal Access", "bullets": [
                "Legal Aid Chatbots: Basic guidance for those without counsel.",
                "Form Filling Assistance: Help complete forms for visas, taxes, small claims.",
                "Civic Education: Explain laws, rights, and obligations."
            ]},
            {"heading": "9. Law Firm Knowledge Management", "bullets": [
                "Internal Document Search: Retrieve memos, briefs, opinions quickly.",
                "Training & Onboarding: Interactive case simulations for juniors.",
                "Best Practices Repository: Auto‑update internal knowledge bases."
            ]},
            {"heading": "10. Intellectual Property (IP) Management", "bullets": [
                "Patent & Trademark Search: Identify potential conflicts before filing.",
                "Filing Assistance: Draft descriptions and claims for patents.",
                "IP Portfolio Monitoring: Track renewals and infringement risks."
            ]},
            {"heading": "11. Due Diligence", "bullets": [
                "M&A Document Review: Summarize large sets of contracts.",
                "Regulatory Risk Checks: Flag licenses, permits, obligations.",
                "Party Background Reports: Compile profiles of entities and individuals."
            ]},
            {"heading": "12. Future Possibilities", "bullets": [
                "Fully Conversational Legal Assistants: Handle initial client intake via conversation.",
                "AI‑Driven Predictive Justice: Forecast probable outcomes.",
                "Real‑Time Contract Negotiation: Assist lawyers in live negotiations."
            ]}
        ],
        "charts": {
            "research_time_saved": {
                "labels": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"],
                "data": [8, 14, 19, 24, 28, 33],
                "title": "Avg. Research Time Saved per Matter (hrs)",
                "type": "line"
            },
            "risk_flags": {
                "labels": ["Liability", "Compliance", "Ambiguity", "Jurisdiction", "IP"],
                "data": [34, 28, 22, 18, 16],
                "title": "Risk Flags by Category (per 100 contracts)",
                "type": "bar"
            },
            "maturity": {
                "labels": ["Research", "Contracts", "Litigation", "Compliance", "KM"],
                "data": [62, 58, 52, 55, 57],
                "title": "Implementation Maturity",
                "type": "radar"
            }
        }
    },
    "logistics": {
        "title": "Logistics",
        "summary": (
            "LLMs evolve from text generators into decision-support systems, knowledge bases, and process optimizers across the "
            "logistics value chain — from warehousing to last‑mile delivery."
        ),
        "sections": [
            {
                "heading": "Extensive Uses of LLMs in Logistics",
                "content": (
                    "Large Language Models (LLMs) are no longer just text generators — they can act as decision-support systems, "
                    "knowledge repositories, process optimizers, and communication hubs in the logistics industry. From warehousing to "
                    "last-mile delivery, their ability to process vast amounts of unstructured and structured data, understand complex "
                    "constraints, and generate actionable insights makes them a transformative force."
                ),
            },
            {
                "heading": "1. Supply Chain Visibility & Tracking",
                "bullets": [
                    "Real-Time Status Reports: Summarize GPS data, IoT sensor feeds, and shipment logs into human-readable updates.",
                    "Predictive Delay Alerts: Analyze weather, traffic, customs data, and historical patterns to warn about delays.",
                    "Dynamic ETAs: Recalculate delivery times continuously based on live conditions and bottlenecks.",
                ],
            },
            {
                "heading": "2. Route Optimization",
                "bullets": [
                    "Multi-Modal Planning: Suggest cost-effective mixes of air, sea, rail, and road with constraints and urgency.",
                    "Adaptive Re-Routing: React to closures, strikes, or congestion and recommend alternatives in real time.",
                    "Energy-Efficient Routing: Minimize carbon emissions without missing deadlines.",
                ],
            },
            {
                "heading": "3. Warehouse Management",
                "bullets": [
                    "Inventory Forecasting: Predict stock shortages or overstock based on demand trends.",
                    "Automated Picking Instructions: Generate optimized picking lists and layouts for robots or workers.",
                    "Shelf Placement Recommendations: Choose storage locations for fast movers using retrieval patterns.",
                ],
            },
            {
                "heading": "4. Procurement & Supplier Management",
                "bullets": [
                    "Supplier Risk Assessment: Read contracts, compliance reports, and news to flag reliability or fraud risks.",
                    "Dynamic Supplier Matching: Recommend alternates during spikes based on performance and proximity.",
                    "Contract Summarization: Condense procurement docs into actionable bullet points.",
                ],
            },
            {
                "heading": "5. Customs & Regulatory Compliance",
                "bullets": [
                    "Automated Document Preparation: Draft bills of lading, invoices, and declarations to regional standards.",
                    "Regulation Monitoring: Scan sources for import/export changes and alert teams.",
                    "Risk Flagging: Detect compliance issues before reaching customs.",
                ],
            },
            {
                "heading": "6. Demand Forecasting & Market Intelligence",
                "bullets": [
                    "Seasonal Pattern Recognition: Predict peak seasons from historical data and market conditions.",
                    "Competitor Analysis: Summarize shipping rates, offerings, and coverage from public sources.",
                    "Disruption Scenarios: Simulate effects of economic shifts or geopolitical events on timelines.",
                ],
            },
            {
                "heading": "7. Customer Service Automation",
                "bullets": [
                    "24/7 Shipment Assistance: Natural-language answers on status, ETAs, and returns.",
                    "Multilingual Support: Translate inquiries and responses instantly.",
                    "Proactive Communication: Notify progress, delays, or rescheduling options automatically.",
                ],
            },
            {
                "heading": "8. Fraud Detection & Security",
                "bullets": [
                    "Pattern Matching for Theft Prevention: Spot unusual patterns indicating pilferage.",
                    "Identity Verification: Cross-check credentials against verified databases.",
                    "Document Authenticity Checks: Flag forged documents via text and metadata analysis.",
                ],
            },
            {
                "heading": "9. Collaboration & Training",
                "bullets": [
                    "Knowledge Base Creation: Compile best practices and training from existing documentation.",
                    "Onboarding Assistance: Interactive Q&A on policies and systems for new hires.",
                    "Cross-Team Coordination: Act as a central information hub across partners and teams.",
                ],
            },
            {
                "heading": "10. Strategic Planning & Optimization",
                "bullets": [
                    "Cost-Benefit Analysis: Compare methods/routes across cost, speed, and risk.",
                    "Sustainability Reporting: Generate carbon reports for ESG compliance.",
                    "Expansion Recommendations: Suggest new markets or hubs via demand heatmaps.",
                ],
            },
            {
                "heading": "11. Advanced AI-Driven Applications",
                "bullets": [
                    "Autonomous Logistics Agents: Bots that negotiate freight, book carriers, and manage paperwork.",
                    "IoT Integration: Interact with sensors to adjust operations dynamically.",
                    "Digital Twin Simulations: Feed data into virtual replicas to test ‘what-if’ scenarios.",
                ],
            },
            {
                "heading": "12. Future Potential",
                "bullets": [
                    "Fully Automated Global Freight Networks: LLMs coordinating autonomous ships, drones, and robots.",
                    "AI-First Logistics Platforms: Conversational interfaces replacing legacy ERPs.",
                    "Predictive Crisis Management: Detect instability or infrastructure risks months in advance.",
                ],
            },
        ],
        "charts": {
            "adoption": {
                "labels": ["Tracking", "Routing", "Warehousing", "Customer Service", "Compliance"],
                "data": [72, 66, 59, 70, 61],
                "title": "AI Adoption by Function (%)",
                "type": "bar"
            },
            "roi": {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "data": [1.1, 1.5, 2.0, 2.6],
                "title": "Modeled ROI Multiplier Over First Year",
                "type": "line"
            },
            "maturity": {
                "labels": ["Data", "Ops", "Evaluation", "Governance", "Automation"],
                "data": [65, 58, 52, 47, 40],
                "title": "Implementation Maturity Radar",
                "type": "radar"
            },
            "cost_breakdown": {
                "labels": ["Inference", "Storage", "Networking", "Labeling", "Training"],
                "data": [46, 12, 9, 8, 25],
                "title": "AI Cost Breakdown (%)",
                "type": "bar"
            },
            "latency": {
                "labels": ["50p", "75p", "90p", "95p", "99p"],
                "data": [320, 460, 680, 880, 1350],
                "title": "End-to-End Latency (ms)",
                "type": "line"
            }
        }
    },
    "gaming": {
        "title": "Gaming",
        "summary": (
            "LLMs augment game development and runtime: powering intelligent NPCs, procedural stories, adaptive encounters,"
            " and real-time game mastering while accelerating tools, QA, and community operations."
        ),
        "sections": [
            {
                "heading": "1. NPC (Non-Player Character) Intelligence",
                "bullets": [
                    "Dynamic Conversations: NPCs hold fluid, context-aware dialogue beyond fixed lines.",
                    "Personality & Memory: Persistent memory lets NPCs recall player choices and evolve traits.",
                    "Adaptive Behavior: Tactics adjust to player strategies; difficulty scales responsively."
                ],
            },
            {
                "heading": "2. Procedural Storytelling",
                "bullets": [
                    "Branching Narratives: Story paths generate in real time from player intent and world state.",
                    "Event Generation: Organic side quests, twists, and emergent world events.",
                    "Lore Expansion: Rich histories, myths, and backstories without manual authoring for every asset."
                ],
            },
            {
                "heading": "3. Quest & Level Design Assistance",
                "bullets": [
                    "Automated Quest Creation: Objectives, dialogue, and rewards consistent with world constraints.",
                    "Dynamic World Building: Context-aware NPCs, dialogs, and encounters populated by progression.",
                    "Environmental Storytelling: Clues, notes, and props tied into the main narrative."
                ],
            },
            {
                "heading": "4. Real-Time Game Mastering",
                "bullets": [
                    "Adaptive Difficulty: Enemies, puzzles, and loot adjust to skill and engagement.",
                    "Virtual Dungeon Master: Narrative orchestration for RPG-style experiences.",
                    "Player Guidance: Hints and tips that preserve immersion and roleplay."
                ],
            },
            {
                "heading": "5. Immersive Dialogue Systems",
                "bullets": [
                    "Emotionally Aware Responses: Tone detection for nuanced NPC reactions.",
                    "Multi-Language Interaction: Speak in any language with immersive translations.",
                    "Voice Integration: TTS empowers living, reactive in-world voices."
                ],
            },
            {
                "heading": "6. Game Content Generation",
                "bullets": [
                    "Weapon & Item Descriptions: Unique names, effects, and lore.",
                    "Enemy Design: New archetypes with mechanics and narrative fit.",
                    "Cultural Diversity: Locations and customs inspired by grounded or fantastical cultures."
                ],
            },
            {
                "heading": "7. Player-Created Content",
                "bullets": [
                    "Modding Support: Assist modders with scripts, dialogue, and compatible lore.",
                    "User Story Mode: Generate scenarios on demand from player prompts.",
                    "AI-Assisted World Building: Co-create environments, dungeons, and quests."
                ],
            },
            {
                "heading": "8. Game Testing & QA",
                "bullets": [
                    "Automated Bug Reporting: Summarize logs, repro steps, and probable fixes.",
                    "Gameplay Balancing: Analyze telemetry and recommend stat/difficulty tweaks.",
                    "Narrative Consistency: Detect plot holes and character inconsistencies early."
                ],
            },
            {
                "heading": "9. Player Support & Community Management",
                "bullets": [
                    "In-Game Help Desk: Answer gameplay questions contextually.",
                    "Toxicity Filtering: Moderate chat with context-aware classifiers.",
                    "Community Summaries: Condense patch notes, forums, and feedback."
                ],
            },
            {
                "heading": "10. Educational & Serious Games",
                "bullets": [
                    "Language Learning: NPC tutors embedded in story and play.",
                    "Simulation Training: Realistic branching scenarios for training sims.",
                    "Historical Accuracy: Authentic dialogue and events for period titles."
                ],
            },
            {
                "heading": "11. Monetization & Player Retention",
                "bullets": [
                    "Personalized Offers: Items/skins tailored to play style and progression.",
                    "Story-Driven Events: Seasonal AI-authored arcs that sustain engagement.",
                    "Interactive Marketing: Talk to in-world characters on social channels."
                ],
            },
            {
                "heading": "12. Future Possibilities",
                "bullets": [
                    "Fully AI-Generated Games: LLMs + procedural engines composing worlds end-to-end.",
                    "Persistent AI Characters: NPCs that recognize players across titles.",
                    "Metaverse Story Weaving: Coordinated events spanning connected worlds."
                ],
            },
        ],
        "charts": {
            "feature_adoption": {
                "labels": ["NPC Dialogue", "Procedural Story", "QA Automation", "Support Bots", "UGC Tools"],
                "data": [78, 64, 55, 61, 49],
                "title": "Feature Adoption in Studios (%)",
                "type": "bar"
            },
            "npc_engagement": {
                "labels": ["W1", "W2", "W3", "W4", "W5"],
                "data": [6.2, 7.4, 8.1, 8.8, 9.3],
                "title": "Avg NPC Conversation Turns per Session",
                "type": "line"
            },
            "maturity": {
                "labels": ["NPC AI", "Story Gen", "Tooling", "QA", "Safety"],
                "data": [62, 58, 50, 46, 52],
                "title": "Implementation Maturity Radar",
                "type": "radar"
            },
            "content_mix": {
                "labels": ["Items", "Quests", "Enemies", "Lore"],
                "data": [35, 25, 20, 20],
                "title": "AI-Generated Content Mix (%)",
                "type": "bar"
            },
            "latency_budget": {
                "labels": ["LLM", "RAG", "Safety", "TTS"],
                "data": [180, 60, 40, 220],
                "title": "Latency Budget by Component (ms)",
                "type": "line"
            }
        }
    },
}


@app.route("/industry/<slug>")
def industry_detail(slug: str):
    key = slug.lower()
    data = INDUSTRIES.get(key)
    if not data:
        return render_template("404.html"), 404
    return render_template("industry_detail.html", industry_key=key, industry=data)


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


@app.route("/api/catalog")
def api_catalog():
    return jsonify(CATALOG)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
