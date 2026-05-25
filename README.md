# 🏍️ Bikes809 - Motorbike Photo Gallery

Bilingvní fotogalerie historických motocyklů s podporou CZ/EN.

**Live web:** https://bikes809.onrender.com/

---

## 📁 Struktura projektu

```
d:\_dev\Bikes809/
├── app.py                          # Hlavní Flask aplikace
├── translations.py                 # CZ/EN překlady
├── requirements.txt                # Python dependencies
├── Procfile                        # Render deployment
├── .gitignore                      # Git konfigurace
├── README.md                       # Tento soubor
└── static/gallery/                 # Fotogalerie
    ├── Aermacchi/
    ├── Jawa/
    └── Suzuki/
```

---

## 🌐 URL Struktura

- `https://bikes809.onrender.com/` - Přesměruje na `/cs/`
- `https://bikes809.onrender.com/cs/` - Česká domovská stránka
- `https://bikes809.onrender.com/en/` - Anglická domovská stránka
- `https://bikes809.onrender.com/cs/Aermacchi/` - Značka (CZ)
- `https://bikes809.onrender.com/cs/Aermacchi/1963.../` - Fotogalerie modelu

**Jazyk switcher** zachovává cestu: `/cs/Aermacchi/` → klikni EN → `/en/Aermacchi/`

---

## 📝 Jak přidat/upravit popis modelu

1. Jdi do složky konkrétního modelu:
   ```
   static/gallery/Jawa/jawa-350-634-sidwcar/
   ```

2. Vytvořit nebo upravit `description.json`:
   ```json
   {
     "cs": "Jawa 350 je legendární československý motocykl...",
     "en": "Jawa 350 is a legendary Czechoslovak motorcycle..."
   }
   ```

3. Ulož a pushnij na GitHub:
   ```bash
   git add .
   git commit -m "Update descriptions"
   git push
   ```

4. **Render automaticky deployuje** - změny se zobrazí za 1-2 minuty

---

## 🖼️ Jak přidat novou fotku

1. Přidej JPG/PNG do modelové složky:
   ```
   static/gallery/Jawa/jawa-350-634-sidwcar/nova-fotka.jpg
   ```

2. Commitni a pushnij:
   ```bash
   git add .
   git commit -m "Add new photos"
   git push
   ```

3. Fotka se automaticky zobrazí v galerii

---

## 🚀 Lokální vývoj

### Instalace:
```bash
cd d:\_dev\Bikes809
pip install -r requirements.txt
```

### Spuštění:
```bash
python app.py
```
Pak jdi na: http://localhost:8080

### Úpravy:
- Úprav HTML/CSS v `app.py` (HTML_LAYOUT sekce)
- Úprav texty v `translations.py`
- Přidej popisy v `description.json`

### Reload:
Flask běží v debug modu - změny se auto-reloadují

---

## 📦 Technologie

- **Backend:** Flask 2.3.0 (Python)
- **Hosting:** Render.com (zdarma)
- **Frontend:** Tailwind CSS
- **Databáze:** JSON soubory (žádná DB)
- **Version control:** Git + GitHub

---

## 🔧 Git cheat sheet

```bash
# Stažení nejnovější verze
git pull

# Přidání a commit změn
git add .
git commit -m "Popis změny"

# Upload na GitHub (trigguje auto-deploy na Render)
git push

# Kontrola stavu
git status

# Poslední commity
git log --oneline
```

---

## 📋 Modely v galerii

### Aermacchi (3x)
- 1963 AERMACCHI HARLEY-DAVIDSON 250 S ALA D'ORO
- 1969 AERMACCHI HARLEY-DAVIDSON 350 ALA D'ORO
- 1974 HARLEY DAVIDSON 250 RR

### Jawa (2x)
- jawa-350-634-sidcar
- jawa-354-side

### Suzuki (2x)
- 1974 Suzuki GT550L
- 1987 Suzuki RG500 PETROL Manual

---

## 🔐 Přihlašování

Vše je součástí veřejného GitHub repozitáře:
- GitHub: ice809/Bikes809
- Email: jan.vicher@vivicta.com

---

## 🎯 Budoucí features (nápady)

- [ ] Lightbox (modal fotky s keyboard nav)
- [ ] Image optimization (thumbnails)
- [ ] Analytics
- [ ] Vlastní doména
- [ ] Popisy u jednotlivých fotek
- [ ] Search/filter
- [ ] Komentáře

---

## 📞 Kontakt

GitHub: https://github.com/ice809/Bikes809
Live: https://bikes809.onrender.com/

---

**Poslední update:** 2026-05-25
