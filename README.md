# NovaForge AI — Storefront

A sleek, black-and-white, Apple-like storefront to sell LLMs and Image Generation models. Built with Flask.

## Features
- Ultra-clean black/white gradient design with glassmorphism
- Product catalog (LLMs and image models)
- Product pages, cart, and mock checkout
- Contact form and auth placeholders
- Responsive and accessible

## Run locally
```bash
# 1) Create virtual env (Windows PowerShell)
python -m venv .venv
. .venv/Scripts/Activate.ps1

# 2) Install dependencies
pip install -r requirements.txt

# 3) Start the server
python main.py
```
Visit http://127.0.0.1:5000

## Customize
- Edit `main.py` to change products or add real auth/checkout.
- Update styles in `static/css/styles.css`.
- Templates live in `templates/`.
