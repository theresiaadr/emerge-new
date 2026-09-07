# PRD — Web Report Sales Srikaton (Django, Phase 1)

## Problem statement (asli)
Aplikasi web Django (project terpisah, DB sendiri) di report.srikaton.id, konsisten dengan pola & desain servis-srikaton.
Model: User(4 role) · Instansi · Kunjungan · FollowUpWA · field terenkripsi · unik instansi case-insensitive.
Views: login/logout, dashboard (per role), kunjungan list/baru/edit/detail, cek_instansi (AJAX), blast_wa, klik_wa (POST), export_excel, hitung_reminder.
Patch wajib: N-1 (AXES_LOCKOUT_PARAMETERS=["username"] + SILENCED_SYSTEM_CHECKS axes.W006), N-2 (crypto hard-fail saat DEBUG=0 & key kosong), AI-1b (captcha di login).
User memilih: kode dibuat ulang dari spec (repo lama tidak tersedia), password buat_akun dari env DEFAULT_PASSWORD (fallback --password), preview pakai SQLite.

## Arsitektur
- `/app/backend` = project Django (`config/`, `report/`, `templates/`, `static/css/app.css`), SQLite di preview, PostgreSQL bila `DB_HOST` diisi.
- Preview: `server.py` = ASGI wrapper (uvicorn port 8001) yang melayani Django di bawah prefix `/api` (root_path) + static via Starlette. Produksi: gunicorn `config.wsgi`/`config.asgi` di root, whitenoise untuk static.
- Frontend React hanya redirect `/` → `/api/`.
- Django 5.2 LTS (Python 3.11 di env; Django 6.0 butuh Python ≥3.12 — kode kompatibel).

## Personas
- Sales (Utoro, Maryadi): catat kunjungan, blast WA, lihat data sendiri.
- Admin/SPV (Devy, Mia): dashboard rekap, filter, export Excel, read-only.
- Superuser (Clyde): admin Django.

## Implemented (2026-06)
- Models, crypto_fields (N-2), wa_templates, context_processors, forms (LoginForm+captcha, KunjunganForm.simpan get_or_create iexact), views lengkap, urls, admin, command `buat_akun` (idempotent) + `seed_demo`.
- Settings: axes N-1, captcha, security headers, Sentry opsional, PostgreSQL/SQLite.
- Templates: base (sidebar maroon 236px + motif kotak + bell reminder), login glassmorphism, dashboard_sales, dashboard_spv (filter, 4 stat, bar chart CSS, tabel), kunjungan_list/form (AJAX cek_instansi + autofill + datalist)/detail (cust-info gold + timeline), blast_wa (POST H0/H2/H5, badge reminder), lockout.
- CSS design system (maroon/gold/ivory, Plus Jakarta Sans, 6 warna badge status).
- Tests: 27 unit test hijau; testing agent e2e 20/20 + UI lolos (iteration_1).
- `check --deploy` bersih dengan env produksi.

## Backlog
- P1: Phase 2 Modul Teknisi (role sudah ada).
- P2: pagination tabel, filter tanggal rentang, pengaturan template WA via admin, reset password self-service.
- Catatan: captcha `DJANGO_CAPTCHA_TEST_MODE=1` hanya untuk preview; set 0 di produksi.
