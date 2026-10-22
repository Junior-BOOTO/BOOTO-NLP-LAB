import base64
import io
import json
import os
import zipfile
from datetime import datetime
from urllib.parse import urlparse

import streamlit as st
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

AUTHOR = "Junior BOOTO WABA"
LANGUAGES = {"Français": "French", "English": "English", "Español": "Spanish"}
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
AUDIO_DOMAINS = {
    "French": ["rfi.fr", "apprendre.tv5monde.com"],
    "English": ["learnenglish.britishcouncil.org", "bbc.co.uk", "learningenglish.voanews.com"],
    "Spanish": ["cervantes.es", "rtve.es"],
}

st.set_page_config(page_title="BOOTO LUDO AI", page_icon="🎲", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.block-container {max-width:1120px;padding-top:2rem;}
.hero {padding:2rem 2.2rem;border-radius:24px;background:linear-gradient(125deg,#211d4c,#5426a7 55%,#a52fb2);color:#fff;margin-bottom:1.5rem;}
.hero h1 {font-family:Manrope,sans-serif;font-size:2.5rem;margin:0 0 .4rem;}
.hero p {font-size:1.08rem;opacity:.92;margin:0;}
.pill {display:inline-block;border:1px solid #ffffff60;border-radius:30px;padding:.3rem .7rem;font-size:.82rem;margin-bottom:.9rem;}
.signature {color:#6b42bc;font-weight:700;}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="hero"><span class="pill">FRANÇAIS · ENGLISH · ESPAÑOL</span><h1>BOOTO LUDO AI</h1><p>Des activités de langue vivantes, ludiques et prêtes à utiliser.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Réglages")
    format_mode = st.selectbox("Format de la fiche", ["Format scolaire PEP", "Fiche libre"], index=0)
    lang_label = st.selectbox("Langue de l’activité", list(LANGUAGES.keys()))
    level = st.selectbox("Niveau CECRL", LEVELS, index=0)
    audience = st.text_input("Public / âge", "Élèves du primaire")
    if format_mode == "Format scolaire PEP":
        school_grade = st.selectbox("Grado / classe", ["Primero", "Segundo", "Tercero", "Cuarto", "Quinto", "Autre"])
        school_period = st.selectbox("Période", ["I", "II", "III"])
        school_year = st.text_input("Année scolaire", "2026")
        school_course = st.text_input("Cours", "")
        school_department = st.text_input("Département / matière", lang_label)
    theme = st.text_input("Thème", "La maison et les meubles")
    objective = st.text_area("Objectif d’apprentissage", "Décrire un lieu et situer des objets")
    duration = st.selectbox("Durée", ["30 minutes", "45 minutes", "60 minutes", "90 minutes"])
    image_model = st.selectbox("Qualité des illustrations", ["Haute (1024 px)", "Très haute (1536 px)"], index=0)
    st.caption("La fiche PEP est le format par défaut. L’audio est fourni par des liens vers des ressources avec des voix humaines, sans voix de synthèse. La création des 20 images HD utilise l’API OpenAI et peut prendre plusieurs minutes.")

st.markdown("#### Une activité dans l’esprit de tes fiches")
st.write("Démarrage visuel, défis progressifs, compréhension, interaction orale, production écrite et évaluation sur 20 points.")

if "activity" not in st.session_state:
    st.session_state.activity = None
if "images" not in st.session_state:
    st.session_state.images = []


def client():
    try:
        key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    except Exception:
        key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        st.error("La clé OPENAI_API_KEY n’est pas encore configurée dans les secrets Render/Streamlit.")
        return None
    return OpenAI(api_key=key, timeout=180.0, max_retries=2)


def generate_activity(api):
    lang = LANGUAGES[lang_label]
    school_mode = format_mode == "Format scolaire PEP"
    if school_mode:
        school_header = {
            "title": f"ACTIVITÉ DU {theme.upper()} - PEP",
            "grade_period_year": f"GRADO {school_grade.upper()} - {school_period} PERIODO - AÑO {school_year}",
            "student_fields": {"Nom": "________________", "COURS": school_course or "________________", "Date": "________________", "Département": school_department},
        }
    else:
        school_header = None
    prompt = f"""Create one original, complete, playful language-teaching activity sheet in {lang}. All learner-facing content must be in {lang}.
Context: CEFR {level}; audience {audience}; theme {theme}; learning objective {objective}; duration {duration}.
School sheet requested: {school_mode}. When true, reproduce this exact school header structure and order: {json.dumps(school_header, ensure_ascii=False)}. Use short worksheet instructions and numbered classroom exercises under the header, followed by any useful learning-resource links. When false, use a clean free-form worksheet. Unless explicitly selected otherwise, the school format is the default.
Pedagogical model: visual vocabulary warm-up; numbered playful tasks; listening comprehension; reading comprehension; oral partner/group game; short written production; differentiated support/challenge; answer key and transparent 20-point rubric. Align vocabulary, grammar, task complexity, and text length to CEFR {level} and {audience}. For listening, include a short transcript/script, but do not create synthetic audio or present generated speech as a real voice. The app will find playable audio lesson pages from established educational broadcasters/publishers that contain human-recorded voices; include a clear audio-resource section in the activity. Provide exactly 20 distinct illustration brief descriptions, each usable as one separate standalone picture and relevant to the tasks. Avoid text inside pictures and copyrighted characters/styles.
Return ONLY valid JSON with keys: title, level, language, theme, objective, duration, materials (array), warmup (string), listening (object with task, script, questions array, answers array), reading (object with passage, task, questions array, answers array), speaking (object with task, steps array, role_cards array), writing (object with task, prompt, success_criteria array), differentiation (object with support, extension), rubric (array of objects with criterion and points), teacher_notes (array), image_briefs (array of exactly 20 strings). Keep everything classroom-ready."""
    response = api.chat.completions.create(
        model=os.getenv("TEXT_MODEL", "gpt-4.1-mini"),
        messages=[{"role": "system", "content": "You are an expert language teacher and activity designer. Produce pedagogically accurate, age-appropriate, playful CEFR-aligned resources. Output valid JSON only."}, {"role": "user", "content": prompt}],
        response_format={"type": "json_object"}, temperature=0.7)
    data = json.loads(response.choices[0].message.content)
    if len(data.get("image_briefs", [])) != 20:
        raise ValueError("Le générateur n’a pas fourni exactement 20 descriptions d’images. Réessaie.")
    data["school_format"] = school_mode
    data["school_header"] = school_header
    data["audio_links"] = find_audio_links(api, lang, level, theme, objective)
    return data


def find_audio_links(api, lang, cefr, lesson_theme, lesson_objective):
    """Find source-page links for real recorded voices; accept URLs only from search citations."""
    domains = AUDIO_DOMAINS[lang]
    try:
        response = api.responses.create(
            model=os.getenv("SEARCH_MODEL", "gpt-4.1-mini"),
            tools=[{"type": "web_search", "filters": {"allowed_domains": domains}}],
            tool_choice="required",
            input=(f"Find up to three current, playable educational audio lesson pages in {lang}, suitable for CEFR {cefr}, "
                   f"related to the theme {lesson_theme} and objective {lesson_objective}. Only choose pages that feature "
                   "human-recorded voices (teachers, speakers, interviews, stories, or native speakers), never text-to-speech. "
                   "Use results from the allowed educational broadcaster/publisher domains. Return a brief list with the page "
                   "title and why it matches; do not invent or rewrite any URLs."),
        )
    except Exception:
        return []
    links, seen = [], set()
    for item in response.output:
        payload = item.model_dump() if hasattr(item, "model_dump") else item
        for content in payload.get("content", []):
            for annotation in content.get("annotations", []):
                cite = annotation.get("url_citation", annotation)
                url = cite.get("url")
                host = (urlparse(url).hostname or "").lower() if url else ""
                if not url or url in seen or not any(host == d or host.endswith("." + d) for d in domains):
                    continue
                seen.add(url)
                links.append({"title": cite.get("title") or "Audio authentique", "url": url})
                if len(links) == 3:
                    return links
    return links


def watermark(image_bytes, label):
    im = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    band_h = max(44, im.width // 18)
    band = Image.new("RGBA", (im.width, band_h), (16, 16, 25, 176))
    draw = ImageDraw.Draw(band)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", max(18, im.width // 38))
    except OSError:
        font = ImageFont.load_default()
    caption = f"{label}  |  {AUTHOR}"
    draw.text((16, band_h // 2), caption, fill=(255, 255, 255, 255), font=font, anchor="lm")
    im.alpha_composite(band, (0, im.height - band_h))
    out = io.BytesIO()
    im.convert("RGB").save(out, format="PNG", optimize=True)
    return out.getvalue()


def image_bytes(api, brief, lang, theme, index, size):
    prompt = (f"Create a single polished educational illustration for a {lang} language-learning worksheet about {theme}. "
              f"Scene {index}: {brief}. Friendly, clear, expressive, high-quality editorial children's-book illustration, "
              "balanced colors, uncluttered composition, suitable for classroom use. No letters, words, labels, logos, "
              "watermarks, or recognizable copyrighted characters. One scene only.")
    result = api.images.generate(model=os.getenv("IMAGE_MODEL", "gpt-image-1.5"), prompt=prompt,
                                 size=size, quality="high", output_format="png")
    return watermark(base64.b64decode(result.data[0].b64_json), f"Illustration {index:02d}")


def render_activity(data):
    def section(title, value):
        st.markdown(f"### {title}")
        if isinstance(value, str):
            st.write(value)
        elif isinstance(value, dict):
            for k, v in value.items():
                st.markdown(f"**{k.replace('_', ' ').capitalize()}**")
                if isinstance(v, list):
                    for item in v: st.markdown(f"- {item}")
                else: st.write(v)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    st.markdown("- " + " · ".join(f"**{k}:** {v}" for k, v in item.items()))
                else: st.markdown(f"- {item}")
    if data.get("school_format"):
        header = data.get("school_header") or {}
        st.markdown(f"## {header.get('title', 'ACTIVITÉ - PEP')}")
        st.markdown(f"**{header.get('grade_period_year', '')}**")
        fields = header.get("student_fields", {})
        st.markdown("  ·  ".join(f"**{key} :** {value}" for key, value in fields.items()))
    else:
        st.markdown(f"## {data.get('title','Activité')}  ·  {data.get('level',level)}")
    st.caption(f"{data.get('language',lang_label)} · {data.get('theme',theme)} · {data.get('level',level)} · {data.get('duration',duration)}")
    st.markdown(f"**Objectif :** {data.get('objective','')}")
    section("Matériel", data.get("materials", []))
    section("1 · Observe et mémorise", data.get("warmup", ""))
    section("2 · Mission écoute", data.get("listening", {}))
    st.markdown("**Audio avec voix réelle**")
    if data.get("audio_links"):
        for link in data["audio_links"]:
            st.markdown(f"- [{link['title']}]({link['url']})")
        st.caption("Liens de ressources audio trouvés sur des sites éducatifs/broadcast; vérifie le lecteur avant la séance. Aucun audio de synthèse n’est utilisé.")
    else:
        st.warning("Aucun lien audio authentique n’a été trouvé pour cette recherche. Relance la création afin d’en chercher un autre.")
    section("3 · Défi lecture", data.get("reading", {}))
    section("4 · Jeu oral", data.get("speaking", {}))
    section("5 · Production écrite", data.get("writing", {}))
    section("Différenciation", data.get("differentiation", {}))
    section("Barème sur 20", data.get("rubric", []))
    section("Notes pour l’enseignant", data.get("teacher_notes", []))
    st.markdown(f'<p class="signature">Créé pour la classe · {AUTHOR}</p>', unsafe_allow_html=True)


def activity_markdown(data):
    header = data.get("school_header") or {}
    title = header.get("title") if data.get("school_format") else data.get("title", "Activité")
    lines = [f"# {title}"]
    if data.get("school_format"):
        lines.append(f"**{header.get('grade_period_year', '')}**")
        lines.extend([f"**{k} :** {v}" for k, v in (header.get("student_fields") or {}).items()])
    lines.extend([f"**Niveau :** {data.get('level', level)}  ·  **Langue :** {data.get('language', lang_label)}  ·  **Durée :** {data.get('duration', duration)}", f"**Thème :** {data.get('theme', theme)}", f"**Objectif :** {data.get('objective', '')}", ""])
    def add(title, value):
        lines.extend([f"## {title}", ""])
        if isinstance(value, dict):
            for key, item in value.items():
                lines.append(f"### {key.replace('_', ' ').capitalize()}")
                if isinstance(item, list): lines.extend([f"- {entry}" for entry in item])
                else: lines.append(str(item))
                lines.append("")
        elif isinstance(value, list):
            for entry in value:
                if isinstance(entry, dict) and entry.get("url"):
                    lines.append(f"- [{entry.get('title', 'Audio')} ]({entry['url']})")
                elif isinstance(entry, dict):
                    lines.append("- " + " · ".join(f"{k}: {v}" for k, v in entry.items()))
                else:
                    lines.append(f"- {entry}")
        else: lines.append(str(value))
        lines.append("")
    add("Matériel", data.get("materials", []))
    add("1 · Observe et mémorise", data.get("warmup", ""))
    add("2 · Mission écoute", data.get("listening", {}))
    add("Audio avec voix réelle", data.get("audio_links", []))
    add("3 · Défi lecture", data.get("reading", {}))
    add("4 · Jeu oral", data.get("speaking", {}))
    add("5 · Production écrite", data.get("writing", {}))
    add("Différenciation", data.get("differentiation", {}))
    add("Barème sur 20", data.get("rubric", []))
    add("Notes pour l’enseignant", data.get("teacher_notes", []))
    lines.append(f"Créé pour la classe · {AUTHOR}")
    return "\n".join(lines)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("✨ Créer l’activité", type="primary", use_container_width=True):
        api = client()
        if api:
            try:
                with st.spinner("Création de l’activité pédagogique…"):
                    st.session_state.activity = generate_activity(api)
                    st.session_state.images = []
                st.success("Activité prête. Vérifie-la, puis lance la création des illustrations.")
            except Exception as exc:
                st.error(f"La génération a échoué : {exc}")
with col2:
    if st.button("🎨 Générer les 20 images HD", use_container_width=True, disabled=not st.session_state.activity):
        api = client()
        if api:
            data = st.session_state.activity
            size = "1536x1024" if image_model.startswith("Très") else "1024x1024"
            bar = st.progress(0, text="Préparation des illustrations…")
            out = []
            for i, brief in enumerate(data["image_briefs"], 1):
                try:
                    out.append(image_bytes(api, brief, data["language"], data["theme"], i, size))
                    bar.progress(i / 20, text=f"Illustration {i}/20 créée et signée")
                except Exception as exc:
                    st.error(f"Échec à l’illustration {i} : {exc}. Les images déjà créées sont conservées.")
                    break
            st.session_state.images = out
            if len(out) == 20:
                st.success("Les 20 illustrations HD signées sont prêtes.")

if st.session_state.activity:
    data = st.session_state.activity
    st.divider()
    st.download_button("⬇ Télécharger la fiche d’activité (.md)", activity_markdown(data), file_name="activite_booto_ludo.md", mime="text/markdown")
    render_activity(data)
    if st.session_state.images:
        st.markdown("### Galerie des illustrations")
        for start in range(0, len(st.session_state.images), 4):
            cols = st.columns(4)
            for col, pos in zip(cols, range(start, min(start + 4, len(st.session_state.images)))):
                with col:
                    st.image(st.session_state.images[pos], caption=data["image_briefs"][pos], use_container_width=True)
        manifest = {"creator": AUTHOR, "generated_at": datetime.utcnow().isoformat() + "Z", "activity": data}
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("activite.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            archive.writestr("fiche_activite.md", activity_markdown(data))
            for i, image in enumerate(st.session_state.images, 1):
                archive.writestr(f"images/illustration_{i:02d}.png", image)
        st.download_button("⬇ Télécharger le dossier complet (activité + 20 images)", zip_buffer.getvalue(), file_name="booto_ludo_activite.zip", mime="application/zip", type="primary")
    else:
        st.info("L’activité est prête. Génère ensuite les 20 images pour obtenir le dossier complet.")

st.divider()
st.caption(f"BOOTO LUDO AI · Conception pédagogique attribuée à {AUTHOR} · Les contenus générés doivent être relus avant utilisation en classe.")
