import os
import socket
import json
from datetime import datetime, timedelta
from flask import Flask, render_template_string, abort, send_from_directory, redirect, url_for, request
from translations import get_translations

app = Flask(__name__)

# --- KONFIGURACE POČÍTADLA ---
VISITS_FILE = os.path.join(os.path.dirname(__file__), 'visits.json')

def load_visits():
    """Načte počty návštěv ze souboru."""
    if os.path.exists(VISITS_FILE):
        try:
            with open(VISITS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_visits(data):
    """Uloží počty návštěv do souboru."""
    with open(VISITS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def increment_visits():
    """Zvýší počítadlo pro dnešní den."""
    today = datetime.now().strftime('%Y-%m-%d')
    visits = load_visits()
    visits[today] = visits.get(today, 0) + 1
    save_visits(visits)
    return visits

# --- KONFIGURACE CESTY ---
# Python teď míří přímo do složky, kde začínají značky (Suzuki, Yamaha atd.)
GALLERY_ROOT = os.path.join(os.path.dirname(__file__), 'static', 'gallery') 

def get_images(path):
    """Získá všechny obrázky ve složce."""
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
    if not os.path.exists(path):
        return []
    try:
        # Bere i soubory s velkými příponami (.JPG)
        files = [f for f in os.listdir(path) if f.lower().endswith(valid_exts) and not f.startswith('.')]
        return sorted(files)
    except OSError:
        return []

def get_description(path, lang='cs'):
    """Čte description.json ze složky."""
    desc_file = os.path.join(path, 'description.json')
    if os.path.exists(desc_file):
        try:
            with open(desc_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                value = data.get(lang, data.get('cs', ''))
                return ''.join(value) if isinstance(value, list) else value
        except:
            return ''
    return ''

@app.route('/media/<path:filename>')
def serve_image(filename):
    """Servíruje fotky přímo z tvého disku."""
    return send_from_directory(GALLERY_ROOT, filename, as_attachment=False)

# Industrial Garage UI - Optimized for High Resolution
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="{{ lang }}" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | MOTOBASE</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Oswald:wght@700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #050505; color: #a1a1aa; }
        .heading-font { font-family: 'Oswald', sans-serif; }
        .full-res-img { image-rendering: -webkit-optimize-contrast; image-rendering: crisp-edges; }
    </style>
</head>
<body>
    <nav class="sticky top-0 z-50 bg-black/95 border-b border-white/5 backdrop-blur-md p-4">
        <div class="max-w-screen-2xl mx-auto flex justify-between items-center px-4">
            <a href="/{{ lang }}/" class="flex items-center gap-2">
                <div class="w-8 h-8 bg-orange-600 flex items-center justify-center font-black text-black italic text-xl">M</div>
                <span class="text-xl font-black text-white uppercase italic tracking-tighter">{{ motobase }}</span>
            </a>
            <div class="flex items-center gap-4">
                <span class="text-[9px] text-zinc-600 font-mono hidden md:block uppercase tracking-widest italic">{{ high_fidelity_mode }}</span>
                <div class="flex gap-2 ml-4 pl-4 border-l border-white/10">
                    <a href="/cs{{ rest_path }}" class="text-[9px] font-black uppercase px-2 py-1 rounded transition {% if lang == 'cs' %}bg-orange-600 text-black{% else %}text-zinc-600 hover:text-white{% endif %}">CZ</a>
                    <a href="/en{{ rest_path }}" class="text-[9px] font-black uppercase px-2 py-1 rounded transition {% if lang == 'en' %}bg-orange-600 text-black{% else %}text-zinc-600 hover:text-white{% endif %}">EN</a>
                </div>
            </div>
        </div>
    </nav>
    <main class="max-w-screen-2xl mx-auto p-4 md:p-12">
        {% block content %}{% endblock %}
    </main>
    <footer class="p-12 text-center border-t border-white/5 mt-20">
        <p class="text-[10px] uppercase tracking-[0.5em] text-zinc-800 font-bold italic">{{ moto_storage }}</p>
    </footer>
</body>
</html>
"""

@app.route('/')
def root():
    """Redirect root na /cs/ (výchozí jazyk)"""
    return redirect('/cs/')

@app.route('/<lang>/')
def home(lang):
    if lang not in ['cs', 'en']:
        abort(404)
    
    # Inkrementuj počítadlo návštěv
    visits = increment_visits()
    total_visits = sum(visits.values())
    today_visits = visits.get(datetime.now().strftime('%Y-%m-%d'), 0)
    
    t = get_translations(lang)
    rest_path = '/'
    
    if not os.path.exists(GALLERY_ROOT):
        return f"ERROR: Path '{GALLERY_ROOT}' does not exist."
    
    brands = sorted([d for d in os.listdir(GALLERY_ROOT) if os.path.isdir(os.path.join(GALLERY_ROOT, d)) and not d.startswith('.')])
    
    content = """
    <div class="flex justify-between items-start mb-12">
        <h1 class="heading-font text-7xl md:text-9xl text-white uppercase italic tracking-tighter opacity-90 leading-none">{{ garaze }}</h1>
        <a href="/{{ lang }}/stats" class="bg-orange-600 hover:bg-orange-700 text-black font-black px-6 py-3 text-sm uppercase tracking-wider transition">
            📊 {{ pocitadlo }}: <span class="text-lg">{{ total_visits }}</span>
        </a>
    </div>
    
    {% if not brands %}
    <div class="bg-zinc-900 border border-white/5 p-8 text-center">
        <p class="text-orange-500 font-bold uppercase tracking-widest">Database Empty</p>
        <p class="text-xs mt-2 italic text-zinc-600">{{ no_brands }} {{ root_path }}</p>
    </div>
    {% else %}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {% for brand in brands %}
        <a href="/{{ lang }}/{{ brand }}" class="group bg-zinc-900/40 border border-white/5 p-16 flex flex-col items-center justify-center hover:border-orange-500 hover:bg-zinc-900 transition-all duration-500 relative overflow-hidden">
            <div class="absolute top-0 left-0 w-1 h-0 bg-orange-600 group-hover:h-full transition-all duration-500"></div>
            <span class="text-5xl font-black uppercase italic group-hover:text-white transition z-10 tracking-tighter">{{ brand }}</span>
            <div class="mt-4 text-[9px] font-bold text-zinc-700 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition duration-500">{{ explore_archive }} &rarr;</div>
        </a>
        {% endfor %}
    </div>
    {% endif %}
    """
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', content), 
                                brands=brands, root_path=GALLERY_ROOT, title=t['garaze'], lang=lang, rest_path=rest_path,
                                motobase=t['motobase'], high_fidelity_mode=t['high_fidelity_mode'], 
                                moto_storage=t['moto_storage'], garaze=t['garaze'], no_brands=t['no_brands'],
                                explore_archive=t['explore_archive'], total_visits=total_visits, today_visits=today_visits,
                                pocitadlo=t.get('pocitadlo', 'Počítadlo'))

@app.route('/<lang>/<brand>')
def brand_detail(lang, brand):
    if lang not in ['cs', 'en']:
        abort(404)
        # Inkrementuj počítadlo
    increment_visits()
        t = get_translations(lang)
    rest_path = f'/{brand}'
    brand_path = os.path.join(GALLERY_ROOT, brand)
    if not os.path.exists(brand_path): abort(404)
    
    models = sorted([d for d in os.listdir(brand_path) if os.path.isdir(os.path.join(brand_path, d)) and not d.startswith('.')])
    previews = {}
    descriptions = {}
    
    for m in models:
        model_dir = os.path.join(brand_path, m)
        images = get_images(model_dir)
        previews[m] = images[0] if images else None
        descriptions[m] = get_description(model_dir, lang)

    content = """
    <div class="mb-20">
        <a href="/{{ lang }}/" class="text-zinc-600 hover:text-white text-[10px] uppercase tracking-widest font-black transition mb-4 inline-block">&larr; {{ back_to_garage }}</a>
        <h1 class="text-8xl md:text-[10rem] font-black text-white uppercase italic tracking-tighter mt-4 leading-none">{{ brand }}</h1>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        {% for model, cover in previews.items() %}
        <a href="/{{ lang }}/{{ brand }}/{{ model }}" class="bg-zinc-900/20 border border-white/5 overflow-hidden hover:border-orange-600/50 transition group">
            <div class="aspect-video bg-black overflow-hidden grayscale group-hover:grayscale-0 transition duration-1000">
                {% if cover %}
                <img src="/media/{{ brand }}/{{ model }}/{{ cover }}" class="w-full h-full object-cover group-hover:scale-105 transition duration-1000">
                {% else %}
                <div class="w-full h-full flex items-center justify-center text-[10px] uppercase text-zinc-800 font-bold">{{ no_high_res_data }}</div>
                {% endif %}
            </div>
            <div class="p-8 flex flex-col gap-4 border-t border-white/5 bg-zinc-900/40">
                <div class="flex justify-between items-center">
                    <h3 class="text-3xl font-black uppercase italic text-white tracking-tighter">{{ model.replace('-', ' ') }}</h3>
                    <div class="w-12 h-12 border border-white/10 flex items-center justify-center group-hover:bg-orange-600 group-hover:border-orange-600 transition-colors">
                        <span class="text-white text-xl font-bold">&rarr;</span>
                    </div>
                </div>
                {% if descriptions.get(model) %}
                <p class="text-sm text-zinc-400 line-clamp-2">{{ descriptions.get(model) | striptags }}</p>
                {% endif %}
            </div>
        </a>
        {% endfor %}
    </div>
    """
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', content), 
                                brand=brand, models=models, previews=previews, descriptions=descriptions, title=brand, lang=lang, rest_path=rest_path,
                                motobase=t['motobase'], high_fidelity_mode=t['high_fidelity_mode'], 
                                moto_storage=t['moto_storage'], back_to_garage=t['back_to_garage'],
                                no_high_res_data=t['no_high_res_data'])

@app.route('/<lang>/<brand>/<model>')
def model_gallery(lang, brand, model):
    if lang not in ['cs', 'en']:
        abort(404)
    
    # Inkrementuj počítadlo
    increment_visits()
    
    t = get_translations(lang)
    rest_path = f'/{brand}/{model}'
    model_path = os.path.join(GALLERY_ROOT, brand, model)
    photos = get_images(model_path)
    
    # Kontrola na video.mp4
    video = None
    video_path = os.path.join(model_path, 'Video.mp4')
    if os.path.exists(video_path):
        video = 'Video.mp4'
    
    if not photos and not video: abort(404)
    
    description = get_description(model_path, lang)
    
    content = """
    <div class="mb-24">
        <div class="flex gap-4 text-[10px] uppercase font-black tracking-[0.3em] text-zinc-600 mb-8 items-center">
            <a href="/{{ lang }}/" class="hover:text-white transition">{{ garaze }}</a>
            <span class="w-1 h-1 bg-zinc-800 rounded-full"></span>
            <a href="/{{ lang }}/{{ brand }}" class="hover:text-white transition">{{ brand }}</a>
        </div>
        <h1 class="text-7xl md:text-[8rem] font-black text-white uppercase italic tracking-tighter leading-none mb-4">{{ model.replace('-', ' ') }}</h1>
        <div class="flex items-center gap-6 mt-6">
            <div class="h-px w-12 bg-orange-600"></div>
            <p class="text-orange-500 font-black uppercase tracking-[0.4em] text-xs">{{ archive }}: {{ photos|length }} {{ shots_in_quality }}</p>
        </div>
        {% if description %}
        <div class="mt-8 p-6 bg-zinc-900/40 border border-white/5 rounded">
            <div class="text-base leading-relaxed text-zinc-300">{{ description | safe }}</div>
        </div>
        {% endif %}

        {% if video %}
        <div class="mt-16 mb-32">
            <div class="relative bg-zinc-900 shadow-[0_0_100px_rgba(0,0,0,0.9)] border border-white/5 overflow-hidden">
                <video controls class="w-full h-auto" style="max-height: 600px;">
                    <source src="/media/{{ brand }}/{{ model }}/{{ video }}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Mřížka náhledů pro rychlou navigaci -->
    <div class="mb-32">
        <div class="grid grid-cols-4 md:grid-cols-8 lg:grid-cols-12 gap-2">
            {% for photo in photos %}
            <a href="#photo-{{ loop.index }}" class="aspect-square bg-zinc-900 border border-white/5 overflow-hidden hover:border-orange-600 transition group">
                <img src="/media/{{ brand }}/{{ model }}/{{ photo }}" class="w-full h-full object-cover opacity-20 group-hover:opacity-100 transition duration-300">
            </a>
            {% endfor %}
        </div>
    </div>

    <!-- Hlavní feed fotek -->
    <div class="flex flex-col gap-32 md:gap-64">
        {% for photo in photos %}
        <div id="photo-{{ loop.index }}" class="group scroll-mt-32">
            <div class="relative bg-zinc-900 shadow-[0_0_100px_rgba(0,0,0,0.9)] border border-white/5">
                <img src="/media/{{ brand }}/{{ model }}/{{ photo }}" 
                     class="w-full h-auto full-res-img block" 
                     loading="lazy"
                     alt="{{ photo }}">
                
                <!-- Tlačítko pro skutečné maximální rozlišení -->
                <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition duration-300">
                    <a href="/media/{{ brand }}/{{ model }}/{{ photo }}" target="_blank" class="bg-black/80 backdrop-blur-md text-white text-[10px] font-black px-4 py-2 border border-white/20 hover:bg-orange-600 hover:border-orange-600 transition flex items-center gap-2">
                        <span>{{ open_original }}</span>
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                    </a>
                </div>
            </div>
            <div class="mt-8 flex justify-between items-baseline px-2 border-b border-white/5 pb-6">
                <span class="text-[10px] font-mono text-zinc-700 uppercase tracking-[0.4em] italic">{{ photo }}</span>
                <span class="text-[10px] font-black text-zinc-900 uppercase tracking-widest">{{ master_asset }}{{ "%03d" | format(loop.index) }}</span>
            </div>
        </div>
        {% endfor %}
    </div>

    <div class="mt-60 mb-20 text-center">
        <a href="/{{ lang }}/{{ brand }}" class="inline-block border-2 border-white/5 px-20 py-8 text-[11px] font-black uppercase tracking-[0.6em] hover:bg-white hover:text-black transition-all duration-700">
            {{ back_on_models }}
        </a>
    </div>
    """
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', content), 
                                brand=brand, model=model, photos=photos, video=video, description=description, title=model, lang=lang, rest_path=rest_path,
                                motobase=t['motobase'], high_fidelity_mode=t['high_fidelity_mode'], 
                                moto_storage=t['moto_storage'], garaze=t['garaze'], archive=t['archive'],
                                shots_in_quality=t['shots_in_quality'], open_original=t['open_original'],
                                master_asset=t['master_asset'], back_on_models=t['back_on_models'])

@app.route('/<lang>/stats')
def statistics(lang):
    if lang not in ['cs', 'en']:
        abort(404)
    
    t = get_translations(lang)
    rest_path = '/stats'
    
    visits = load_visits()
    if not visits:
        visits = {datetime.now().strftime('%Y-%m-%d'): 0}
    
    # Příprava dat
    today = datetime.now().strftime('%Y-%m-%d')
    today_visits = visits.get(today, 0)
    total_visits = sum(visits.values())
    
    # Posledních 30 dní
    last_30_days = {}
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        last_30_days[date] = visits.get(date, 0)
    
    # Posledních 7 dní
    last_7_days = {}
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        last_7_days[date] = visits.get(date, 0)
    
    # Týdenní agregace (posledních 12 týdnů)
    weekly_data = {}
    for i in range(12):
        week_start = datetime.now() - timedelta(days=7*i)
        week_key = f"W{week_start.strftime('%U')}"
        week_visits = 0
        for j in range(7):
            date = (week_start - timedelta(days=j)).strftime('%Y-%m-%d')
            week_visits += visits.get(date, 0)
        weekly_data[week_key] = week_visits
    
    # Měsíční agregace
    monthly_data = {}
    for i in range(12):
        month_start = datetime.now() - timedelta(days=30*i)
        month_key = month_start.strftime('%Y-%m')
        month_visits = 0
        for j in range(30):
            date = (month_start - timedelta(days=j)).strftime('%Y-%m-%d')
            month_visits += visits.get(date, 0)
        monthly_data[month_key] = month_visits
    
    content = """
    <div class="mb-12">
        <a href="/{{ lang }}/" class="text-zinc-600 hover:text-white text-xs uppercase tracking-widest font-black transition mb-4 inline-block">&larr; {{ back }}</a>
        <h1 class="text-6xl md:text-8xl font-black text-white uppercase italic tracking-tighter mt-4 leading-none">{{ statistika }}</h1>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
        <div class="bg-zinc-900/40 border border-white/5 p-8 rounded">
            <div class="text-zinc-400 text-xs uppercase tracking-widest mb-2">{{ dnes }}</div>
            <div class="text-5xl font-black text-orange-500">{{ today_visits }}</div>
        </div>
        <div class="bg-zinc-900/40 border border-white/5 p-8 rounded">
            <div class="text-zinc-400 text-xs uppercase tracking-widest mb-2">{{ tyzden }}</div>
            <div class="text-5xl font-black text-orange-500">{{ week_visits }}</div>
        </div>
        <div class="bg-zinc-900/40 border border-white/5 p-8 rounded">
            <div class="text-zinc-400 text-xs uppercase tracking-widest mb-2">{{ celkem }}</div>
            <div class="text-5xl font-black text-orange-500">{{ total_visits }}</div>
        </div>
    </div>
    
    <div class="space-y-16">
        <div class="bg-zinc-900/40 border border-white/5 p-8 rounded">
            <h2 class="text-2xl font-black uppercase tracking-tighter mb-6">📈 {{ poslednych_7_dni }}</h2>
            <canvas id="chart7days" height="80"></canvas>
        </div>
        
        <div class="bg-zinc-900/40 border border-white/5 p-8 rounded">
            <h2 class="text-2xl font-black uppercase tracking-tighter mb-6">📊 {{ poslednych_30_dni }}</h2>
            <canvas id="chart30days" height="60"></canvas>
        </div>
        
        <div class="bg-zinc-900/40 border border-white/5 p-8 rounded">
            <h2 class="text-2xl font-black uppercase tracking-tighter mb-6">📅 {{ tydny }}</h2>
            <canvas id="chartWeekly" height="60"></canvas>
        </div>
        
        <div class="bg-zinc-900/40 border border-white/5 p-8 rounded">
            <h2 class="text-2xl font-black uppercase tracking-tighter mb-6">🗓️ {{ mesice }}</h2>
            <canvas id="chartMonthly" height="60"></canvas>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // 7 dní
        const ctx7 = document.getElementById('chart7days').getContext('2d');
        new Chart(ctx7, {
            type: 'line',
            data: {
                labels: {{ labels_7days | tojson }},
                datasets: [{
                    label: '{{ navstev }}',
                    data: {{ data_7days | tojson }},
                    borderColor: '#ea580c',
                    backgroundColor: 'rgba(234, 88, 12, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#a1a1a1' }, grid: { color: '#27272a' } },
                    x: { ticks: { color: '#a1a1a1' }, grid: { color: '#27272a' } }
                }
            }
        });
        
        // 30 dní
        const ctx30 = document.getElementById('chart30days').getContext('2d');
        new Chart(ctx30, {
            type: 'bar',
            data: {
                labels: {{ labels_30days | tojson }},
                datasets: [{
                    label: '{{ navstev }}',
                    data: {{ data_30days | tojson }},
                    backgroundColor: '#ea580c'
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#a1a1a1' }, grid: { color: '#27272a' } },
                    x: { ticks: { color: '#a1a1a1' }, grid: { color: '#27272a' } }
                }
            }
        });
        
        // Týdny
        const ctxWeekly = document.getElementById('chartWeekly').getContext('2d');
        new Chart(ctxWeekly, {
            type: 'line',
            data: {
                labels: {{ labels_weekly | tojson }},
                datasets: [{
                    label: '{{ navstev }}',
                    data: {{ data_weekly | tojson }},
                    borderColor: '#ea580c',
                    backgroundColor: 'rgba(234, 88, 12, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#a1a1a1' }, grid: { color: '#27272a' } },
                    x: { ticks: { color: '#a1a1a1' }, grid: { color: '#27272a' } }
                }
            }
        });
        
        // Měsíce
        const ctxMonthly = document.getElementById('chartMonthly').getContext('2d');
        new Chart(ctxMonthly, {
            type: 'doughnut',
            data: {
                labels: {{ labels_monthly | tojson }},
                datasets: [{
                    data: {{ data_monthly | tojson }},
                    backgroundColor: ['#ea580c', '#f97316', '#fb923c', '#fed7aa', '#fef3c7', '#fef08a', '#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6', '#1d4ed8', '#1e40af']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#a1a1a1' } } }
            }
        });
    </script>
    
    <div class="mt-16 text-center">
        <a href="/{{ lang }}/" class="inline-block border-2 border-white/5 px-20 py-8 text-xs font-black uppercase tracking-[0.2em] hover:bg-white hover:text-black transition-all duration-700">
            {{ zpatky }}
        </a>
    </div>
    """
    
    # Příprava dat pro Jinja
    labels_7days = list(reversed(list(last_7_days.keys())))
    data_7days = list(reversed(list(last_7_days.values())))
    
    labels_30days = list(reversed(list(last_30_days.keys())))
    data_30days = list(reversed(list(last_30_days.values())))
    
    labels_weekly = list(reversed(list(weekly_data.keys())))
    data_weekly = list(reversed(list(weekly_data.values())))
    
    labels_monthly = list(reversed(list(monthly_data.keys())))
    data_monthly = list(reversed(list(monthly_data.values())))
    
    week_visits = sum(last_7_days.values())
    
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', content),
                                title=t['statistika'], lang=lang, rest_path=rest_path,
                                motobase=t['motobase'], high_fidelity_mode=t['high_fidelity_mode'],
                                moto_storage=t['moto_storage'],
                                statistika=t.get('statistika', 'Statistika'),
                                back=t.get('back', 'Zpět'),
                                dnes=t.get('dnes', 'Dnes'),
                                tyzden=t.get('tyzden', 'Týden'),
                                celkem=t.get('celkem', 'Celkem'),
                                poslednych_7_dni=t.get('poslednych_7_dni', 'Posledních 7 dní'),
                                poslednych_30_dni=t.get('poslednych_30_dni', 'Posledních 30 dní'),
                                tydny=t.get('tydny', 'Týdny'),
                                mesice=t.get('mesice', 'Měsíce'),
                                navstev=t.get('navstev', 'Návštěv'),
                                zpatky=t.get('zpatky', 'Zpět na galárii'),
                                today_visits=today_visits,
                                week_visits=week_visits,
                                total_visits=total_visits,
                                labels_7days=labels_7days,
                                data_7days=data_7days,
                                labels_30days=labels_30days,
                                data_30days=data_30days,
                                labels_weekly=labels_weekly,
                                data_weekly=data_weekly,
                                labels_monthly=labels_monthly,
                                data_monthly=data_monthly)

if __name__ == '__main__':
    # Automatické zjištění lokální IP adresy počítače
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "!"*60)
    print("  MAX-RESOLUTION MOTO GALLERY ENGINE")
    print(f"  INTERNÍ: http://localhost:5000")
    print(f"  EXTERNÍ: http://{local_ip}:5000")
    print("!"*60 + "\n")

    # host='0.0.0.0' umožní přístup z jiných zařízení v síti
    app.run(debug=True, host='0.0.0.0', port=5000)