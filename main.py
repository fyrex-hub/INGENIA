# =============================================================================

# INGENIA — Assistant Clinique Intelligent · Version tout-en-un

# Auteur  : Fabien Barnier — 2026

# Un seul fichier · Streamlit Cloud ready

# =============================================================================

import streamlit as st
import sqlite3
import re
import os
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────

# PROTECTION PAR MOT DE PASSE

# ─────────────────────────────────────────────────────────────────────────────

MOT_DE_PASSE = "ingenia2026"  # ← Changez ce mot de passe si vous le souhaitez

def verifier_acces():
if “acces_autorise” not in st.session_state:
st.session_state[“acces_autorise”] = False

```
if not st.session_state["acces_autorise"]:
    st.markdown("""
    <style>
    .login-box { max-width:380px; margin:80px auto; background:white;
                 border-radius:16px; padding:2.5rem; box-shadow:0 8px 32px rgba(0,0,0,.12); }
    .login-title { font-family:'DM Serif Display',serif; font-size:1.8rem;
                   color:#1E3A5F; text-align:center; margin-bottom:.3rem; }
    .login-sub { color:#64748B; font-size:.88rem; text-align:center; margin-bottom:1.5rem; }
    </style>
    <div class="login-box">
        <div style="text-align:center;font-size:2.5rem;">🏥</div>
        <div class="login-title">INGENIA</div>
        <div class="login-sub">Assistant Clinique Intelligent<br>Accès réservé · Fabien Barnier 2026</div>
    </div>
    """, unsafe_allow_html=True)

    mdp = st.text_input("🔑 Mot de passe", type="password", placeholder="Entrez le mot de passe...")
    col1, col2 = st.columns([1, 1])
    if col1.button("Accéder à INGENIA", use_container_width=True, type="primary"):
        if mdp == MOT_DE_PASSE:
            st.session_state["acces_autorise"] = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect.")
    st.caption("⚠️ Application réservée à l'usage professionnel du titulaire.")
    st.stop()
```

verifier_acces()

# ─────────────────────────────────────────────────────────────────────────────

# BASE DE CONNAISSANCES MÉDICALES

# ─────────────────────────────────────────────────────────────────────────────

MOTS_CLES = {
“alimentation”: [“mange pas”,“ne mange pas”,“refuse manger”,“refus alimentaire”,“anorexie”,
“perte appétit”,“appétit diminué”,“pas touché plateau”,“mange peu”,“dénutrition”,
“amaigrissement”,“perte poids”,“mange rien”,“bouche sèche”,“nausée”,“vomissement”,
“vomissements”,“dysphagie”,“fausse route”,“avale mal”,“mange difficilement”],
“hydratation”: [“soif”,“ne boit pas”,“boit peu”,“déshydraté”,“déshydratation”,“bouche sèche”,
“sécheresse”,“urines foncées”,“peu urines”,“diurèse faible”,“pas bu”,“refus boisson”],
“douleur”: [“douleur”,“douleurs”,“mal”,“souffre”,“souffrant”,“gémit”,“grimace”,“crie”,
“agité douleur”,“douloureux”,“EVA”,“échelle douleur”,“antalgique”,“antalgie”,
“se plaint”,“plainte douloureuse”,“position antalgique”],
“agitation”: [“agité”,“agitation”,“s’agite”,“nerveux”,“anxieux”,“angoissé”,“panique”,
“crie”,“pleure”,“frappe”,“résiste”,“opposant”,“agressif”,“agressivité”,
“déambule”,“erre”,“cogite”,“inquiet”,“perturbé”,“nuit agitée”,“nuit difficile”],
“sommeil”: [“dort pas”,“insomnie”,“nuit blanche”,“réveillé”,“ne dort pas”,“trouble sommeil”,
“sommeil agité”,“sommeil perturbé”,“fatigue”,“épuisé”,“somnolent”,“somnolence”,
“dort beaucoup”,“hypersomnie”,“assouplissement”,“agité nuit”],
“chute”: [“chute”,“chuter”,“tombé”,“tombe”,“risque chute”,“a chuté”,“sol”,“par terre”,
“instable”,“déséquilibre”,“marche difficile”,“marche instable”,“vertige”,“vertiges”,
“tituber”,“jambes molles”,“faiblesse membres”],
“peau”: [“rougeur”,“rougeurs”,“escarre”,“escarres”,“plaie”,“plaies”,“lésion”,“lésions cutanées”,
“macération”,“peau rouge”,“sacrum”,“talon”,“fesses”,“dos”,“effritement”,“ulcère”,
“ulcération”,“peau fragilisée”,“érythème”,“suintement”],
“confusion”: [“confus”,“confusion”,“désorienté”,“désorientation”,“ne reconnaît plus”,
“perdu”,“ne sait plus”,“hallucination”,“hallucine”,“voit des choses”,“parle seul”,
“discours incohérent”,“incohérent”,“troublé”,“délirant”,“délire”,“ne répond pas”,
“répond pas”,“propos bizarres”],
“respiration”: [“dyspnée”,“essoufflement”,“essoufflé”,“spo2”,“saturation”,“02”,“oxygène”,
“respire mal”,“difficultés respirer”,“respiration difficile”,“cyanose”,“bleuté”,
“tachypnée”,“polypnée”,“encombrement”,“toux”,“toux grasse”,“crépitants”],
“elimination”: [“constipé”,“constipation”,“diarrhée”,“n’a pas été”,“selles”,“pas de selles”,
“incontinence”,“fuites”,“urine”,“urines”,“n’urine pas”,“rétention”,“anurie”,
“oligurie”,“brûlures urinaires”,“infectieux urinaire”],
“temperature”: [“fièvre”,“fébrile”,“température”,“38”,“39”,“40”,“frissons”,“hyperthermie”,
“chaud”,“brûlant”,“hypothermie”,“froid”,“gelé”,“tremble”],
“mobilite”: [“grabataire”,“alité”,“immobile”,“ne se lève pas”,“marche pas”,“ne marche plus”,
“fauteuil”,“wheelchair”,“transfert difficile”,“aide déplacement”,“contention”,
“membres”,“paralysie”,“parésie”,“hémiplégie”,“raideur”],
“communication”: [“muet”,“ne parle plus”,“aphasie”,“discours”,“langage”,“comprend pas”,
“n’entend pas”,“sourd”,“aveugle”,“isolé”,“repli”,“repli sur soi”,“ne communique plus”]
}

SYNONYMES = {
“n’a pas touché son plateau”: “mange pas”,
“n’a pas mangé”: “mange pas”,
“refus de manger”: “refuse manger”,
“refus alimentaire”: “refuse manger”,
“choqué”: “agité”,
“spo2”: “saturation”,
“o2”: “oxygène”,
“hta”: “hypertension”,
“avc”: “accident vasculaire”,
“imc”: “poids”,
“evn”: “douleur”,
“eva”: “douleur”,
“gl”: “glucose”,
“hb”: “hémoglobine”,
“ta”: “tension artérielle”,
}

ABREVIATIONS = {
“hta”: “hypertension”,
“avc”: “accident vasculaire”,
“imc”: “indice masse corporelle”,
“evn”: “échelle douleur”,
“eva”: “échelle douleur”,
“spo2”: “saturation”,
“ta”: “tension artérielle”,
“fc”: “fréquence cardiaque”,
“fr”: “fréquence respiratoire”,
“t°”: “température”,
}

BESOINS_HENDERSON = {
“respirer”:           {“emoji”: “🫁”, “label”: “Respirer”,                   “mots”: [“dyspnée”,“saturation”,“respiration”,“essoufflement”,“oxygène”,“toux”,“cyanose”]},
“manger”:             {“emoji”: “🍽️”, “label”: “Boire et manger”,            “mots”: [“mange”,“manger”,“appétit”,“alimentation”,“boit”,“hydratation”,“fausse route”,“déglutition”,“anorexie”,“dénutrition”]},
“eliminer”:           {“emoji”: “🚽”, “label”: “Éliminer”,                   “mots”: [“selles”,“urines”,“constipation”,“diarrhée”,“incontinence”,“rétention”]},
“mouvoir”:            {“emoji”: “🦿”, “label”: “Se mouvoir”,                 “mots”: [“marche”,“mobilité”,“déplacement”,“transfert”,“alité”,“chute”,“grabataire”]},
“dormir”:             {“emoji”: “😴”, “label”: “Dormir et se reposer”,       “mots”: [“sommeil”,“dort”,“nuit”,“insomnie”,“agité”,“fatigue”,“somnolent”]},
“vetir”:              {“emoji”: “👔”, “label”: “Se vêtir”,                   “mots”: [“habillage”,“déshabillage”,“autonomie vestimentaire”]},
“temperature”:        {“emoji”: “🌡️”, “label”: “Maintenir la température”,   “mots”: [“fièvre”,“température”,“frissons”,“hyperthermie”,“hypothermie”]},
“hygiene”:            {“emoji”: “🧼”, “label”: “Être propre”,                “mots”: [“hygiène”,“toilette”,“peau”,“escarre”,“rougeur”,“plaie”,“lésion”]},
“securite”:           {“emoji”: “🛡️”, “label”: “Éviter les dangers”,        “mots”: [“chute”,“risque”,“danger”,“confusion”,“agitation”,“désorienté”,“sécurité”]},
“communiquer”:        {“emoji”: “💬”, “label”: “Communiquer”,               “mots”: [“communique”,“parle”,“langage”,“aphasie”,“comprend”,“répond”,“confus”,“désorienté”]},
“valeurs”:            {“emoji”: “⭐”, “label”: “Agir selon ses valeurs”,     “mots”: [“religion”,“spiritualité”,“croyance”,“valeurs”,“rites”]},
“realiser”:           {“emoji”: “🎯”, “label”: “Se réaliser”,               “mots”: [“activité”,“autonomie”,“occupation”,“projet”,“réalisation”]},
“recreer”:            {“emoji”: “🎮”, “label”: “Se recréer”,                “mots”: [“loisir”,“jeu”,“divertissement”,“récréation”,“visite”]},
“apprendre”:          {“emoji”: “📚”, “label”: “Apprendre”,                 “mots”: [“comprend”,“éducation”,“information”,“apprentissage”,“enseignement”]},
}

PROBLEMES_CLINIQUES = {
“malnutrition”: {
“emoji”: “⚠️”, “label”: “Malnutrition / Dénutrition”,
“definition”: “Apport nutritionnel insuffisant compromettant l’état général.”,
“signes”: [“mange pas”,“refus alimentaire”,“perte poids”,“anorexie”,“amaigrissement”,“dénutrition”],
“actions”: [“Peser le patient”, “Compléter la fiche alimentaire”, “Proposer des compléments nutritionnels”, “Alerter l’infirmière sur le refus alimentaire”, “Adapter les textures si besoin”],
“niveau_urgence”: 3
},
“déshydratation”: {
“emoji”: “💧”, “label”: “Risque de déshydratation”,
“definition”: “Apport hydrique insuffisant pouvant altérer l’état général.”,
“signes”: [“boit peu”,“ne boit pas”,“déshydraté”,“bouche sèche”,“urines foncées”],
“actions”: [“Encourager la prise de boissons”, “Tracer les apports hydriques”, “Alerter l’infirmière si refus persistant”, “Proposer des boissons variées et adaptées”],
“niveau_urgence”: 3
},
“chute”: {
“emoji”: “🚨”, “label”: “Risque de chute”,
“definition”: “Risque de chute lié à l’instabilité, la confusion ou la faiblesse.”,
“signes”: [“chute”,“tombé”,“instable”,“vertige”,“marche difficile”,“déséquilibre”],
“actions”: [“Mettre les barrières de lit”, “Laisser la sonnette à portée”, “Adapter l’environnement”, “Surveiller les déplacements”, “Signaler à l’équipe”],
“niveau_urgence”: 4
},
“escarre”: {
“emoji”: “🩹”, “label”: “Risque d’escarre”,
“definition”: “Lésion cutanée par pression sur une zone d’appui.”,
“signes”: [“rougeur”,“escarre”,“plaie”,“lésion”,“sacrum”,“talon”,“peau rouge”,“macération”],
“actions”: [“Changer de position toutes les 2-3h”, “Appliquer les soins de peau prescrits”, “Utiliser le matelas anti-escarres”, “Tracer le score de Braden”, “Alerter l’infirmière”],
“niveau_urgence”: 3
},
“douleur”: {
“emoji”: “😣”, “label”: “Douleur non soulagée”,
“definition”: “Douleur persistante ou insuffisamment traitée.”,
“signes”: [“douleur”,“douleurs”,“mal”,“souffre”,“gémit”,“grimace”,“douloureux”],
“actions”: [“Évaluer la douleur (EVN 0-10)”, “Alerter l’infirmière”, “Adapter la position”, “Appliquer les prescriptions antalgiques”, “Réévaluer après traitement”],
“niveau_urgence”: 3
},
“confusion”: {
“emoji”: “🌀”, “label”: “Syndrome confusionnel”,
“definition”: “État de confusion aiguë nécessitant une évaluation urgente.”,
“signes”: [“confus”,“confusion”,“désorienté”,“hallucination”,“incohérent”,“perdu”,“ne reconnaît plus”],
“actions”: [“Alerter l’infirmière immédiatement”, “Sécuriser l’environnement”, “Rester calme et rassurant”, “Ne pas laisser le patient seul”, “Orienter doucement dans le temps et l’espace”],
“niveau_urgence”: 4
},
“agitation”: {
“emoji”: “⚡”, “label”: “Agitation”,
“definition”: “État d’agitation pouvant traduire une douleur, une confusion ou une angoisse.”,
“signes”: [“agité”,“agitation”,“nerveux”,“agressif”,“crie”,“frappe”,“résiste”],
“actions”: [“Rester calme et apaisant”, “Identifier la cause possible”, “Alerter l’infirmière”, “Sécuriser l’environnement”, “Éviter la contention sauf prescription médicale”],
“niveau_urgence”: 3
},
“trouble_sommeil”: {
“emoji”: “🌙”, “label”: “Troubles du sommeil”,
“definition”: “Perturbation du cycle veille-sommeil affectant la récupération.”,
“signes”: [“dort pas”,“insomnie”,“nuit agitée”,“réveillé”,“nuit blanche”,“sommeil perturbé”],
“actions”: [“Tracer la qualité du sommeil”, “Adapter l’environnement (lumière, bruit)”, “Signaler à l’infirmière”, “Proposer des rituels de coucher”],
“niveau_urgence”: 2
},
“dyspnée”: {
“emoji”: “🫁”, “label”: “Détresse respiratoire”,
“definition”: “Difficulté respiratoire nécessitant une évaluation urgente.”,
“signes”: [“dyspnée”,“essoufflement”,“saturation”,“respire mal”,“cyanose”,“tachypnée”],
“actions”: [“ALERTER L’INFIRMIÈRE EN URGENCE”, “Installer le patient en position assise”, “Surveiller la saturation (SpO2)”, “Rester auprès du patient”],
“niveau_urgence”: 4
},
}

# ─────────────────────────────────────────────────────────────────────────────

# MOTEUR D’ANALYSE NLP

# ─────────────────────────────────────────────────────────────────────────────

def normaliser(texte: str) -> str:
texte = texte.lower().strip()
for abr, val in ABREVIATIONS.items():
texte = re.sub(r’\b’ + abr + r’\b’, val, texte)
for syn, val in SYNONYMES.items():
texte = texte.replace(syn, val)
return texte

def extraire_mots_cles(texte: str) -> list:
texte_norm = normaliser(texte)
detectes = set()
for categorie, mots in MOTS_CLES.items():
for mot in mots:
if mot in texte_norm:
detectes.add(mot)
return sorted(detectes)

def detecter_besoins(mots_cles: list, texte: str) -> list:
texte_norm = normaliser(texte)
besoins_impactes = []
for code, besoin in BESOINS_HENDERSON.items():
for mot in besoin[“mots”]:
if mot in texte_norm or any(mot in mk for mk in mots_cles):
besoins_impactes.append({
“code”: code,
“emoji”: besoin[“emoji”],
“label”: besoin[“label”]
})
break
return besoins_impactes

def detecter_risques(mots_cles: list, texte: str) -> list:
texte_norm = normaliser(texte)
risques = []
for code, probleme in PROBLEMES_CLINIQUES.items():
for signe in probleme[“signes”]:
if signe in texte_norm or any(signe in mk for mk in mots_cles):
risques.append({
“code”: code,
“emoji”: probleme[“emoji”],
“label”: probleme[“label”],
“definition”: probleme[“definition”],
“actions”: probleme[“actions”],
“niveau_urgence”: probleme[“niveau_urgence”]
})
break
return sorted(risques, key=lambda x: -x[“niveau_urgence”])

def calculer_score(risques: list) -> int:
if not risques:
return 1
max_u = max(r[“niveau_urgence”] for r in risques)
return min(max_u, 4)

def generer_plan_actions(risques: list) -> list:
plan = []
seen = set()
for r in risques:
for action in r[“actions”]:
if action not in seen:
seen.add(action)
plan.append({“action”: action, “source”: r[“label”]})
return plan

def generer_transmission(nom: str, age: int, observation: str,
besoins: list, risques: list,
plan: list, score: int) -> dict:
now = datetime.now()
date_str = now.strftime(”%d/%m/%Y à %H:%M”)

```
niveaux = {1: "🟢 Faible", 2: "🟡 Modéré", 3: "🟠 Élevé", 4: "🔴 CRITIQUE"}
alertes = {
    1: "✅ Situation stable — surveillance habituelle",
    2: "ℹ️ Vigilance recommandée — informer l'infirmière",
    3: "⚠️ Situation préoccupante — alerter l'infirmière",
    4: "🚨 URGENCE — alerter l'infirmière IMMÉDIATEMENT"
}

besoins_txt = ", ".join(b["label"] for b in besoins) if besoins else "Aucun besoin spécifique identifié"
risques_txt = ", ".join(r["label"] for r in risques) if risques else "Aucun risque spécifique identifié"
actions_txt = "\n".join(f"  • {p['action']}" for p in plan[:6]) if plan else "  • Surveillance standard"

texte = f"""╔══════════════════════════════════════════════════╗
```

║         TRANSMISSION SOIGNANTE — INGENIA         ║
║          Format DAR · Aide à la réflexion        ║
╚══════════════════════════════════════════════════╝

Patient    : {nom} · {age} ans
Date       : {date_str}
Criticité  : {niveaux.get(score, ‘🟢 Faible’)}

━━━ D — DONNÉES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{observation}

Besoins Henderson impactés :
{besoins_txt}

Risques identifiés :
{risques_txt}

━━━ A — ACTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{actions_txt}

━━━ R — RÉSULTATS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Réévaluation à effectuer après mise en place des actions.
Informer l’équipe lors de la prochaine relève.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚕️  Document d’aide à la réflexion clinique — INGENIA
Généré le {date_str}
⚠️  Validation par un professionnel de santé obligatoire.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━”””

```
return {
    "texte": texte,
    "alerte": alertes.get(score, alertes[1]),
    "niveau": niveaux.get(score, "🟢 Faible")
}
```

def analyser(nom: str, age: int, observation: str) -> dict:
mots = extraire_mots_cles(observation)
besoins = detecter_besoins(mots, observation)
risques = detecter_risques(mots, observation)
score = calculer_score(risques)
plan = generer_plan_actions(risques)
transmission = generer_transmission(nom, age, observation, besoins, risques, plan, score)
return {
“mots_cles”: mots,
“besoins”: besoins,
“risques”: risques,
“score”: score,
“plan”: plan,
“transmission”: transmission,
}

# ─────────────────────────────────────────────────────────────────────────────

# BASE DE DONNÉES SQLite

# ─────────────────────────────────────────────────────────────────────────────

DB_PATH = “ingenia.db”

def init_db():
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute(””“CREATE TABLE IF NOT EXISTS observations (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nom TEXT, age INTEGER, observation TEXT,
score INTEGER, transmission TEXT,
date_obs TEXT DEFAULT (datetime(‘now’,‘localtime’))
)”””)
conn.commit()
conn.close()

def sauvegarder(nom, age, observation, score, transmission):
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute(“INSERT INTO observations (nom,age,observation,score,transmission) VALUES (?,?,?,?,?)”,
(nom, age, observation, score, transmission))
conn.commit()
conn.close()

def historique(nom):
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute(“SELECT * FROM observations WHERE nom=? ORDER BY date_obs DESC”, (nom,))
rows = c.fetchall()
conn.close()
return rows

def liste_patients():
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute(“SELECT DISTINCT nom FROM observations ORDER BY nom”)
rows = [r[0] for r in c.fetchall()]
conn.close()
return rows

def stats():
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
nb_obs = c.execute(“SELECT COUNT(*) FROM observations”).fetchone()[0]
nb_pat = c.execute(“SELECT COUNT(DISTINCT nom) FROM observations”).fetchone()[0]
derniere = c.execute(“SELECT MAX(date_obs) FROM observations”).fetchone()[0]
conn.close()
return {“nb_obs”: nb_obs, “nb_pat”: nb_pat, “derniere”: derniere or “—”}

# ─────────────────────────────────────────────────────────────────────────────

# INTERFACE STREAMLIT

# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title=“INGENIA”, page_icon=“🏥”, layout=“wide”)
init_db()

st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;600&display=swap');
.stApp { background: linear-gradient(135deg,#F0F4F8,#E8EEF4); font-family:'DM Sans',sans-serif; }
.header { background:linear-gradient(135deg,#0A1628,#1E3A5F,#2E6DA4); color:white; padding:1.5rem 2rem;
          border-radius:14px; margin-bottom:1.2rem; }
.header h1 { font-family:'DM Serif Display',serif; font-size:2rem; margin:0; }
.header p  { font-size:0.88rem; opacity:0.75; margin:0.2rem 0 0; }
.card { background:white; border-radius:12px; padding:1.3rem 1.5rem;
        box-shadow:0 2px 10px rgba(0,0,0,.06); margin-bottom:.9rem; }
.card-title { font-weight:700; color:#1E3A5F; margin-bottom:.8rem;
              padding-bottom:.4rem; border-bottom:2px solid #E8EEF4; }
.tag { display:inline-block; background:#EEF4FF; color:#1E3A5F; border:1px solid #C7D9F0;
       padding:.15rem .6rem; border-radius:14px; font-size:.8rem; margin:.15rem; }
.tag-r { background:#FFF7ED; color:#9A3412; border-color:#FDBA74; }
.alerte-1 { background:#F0FDF4; border-left:4px solid #22C55E; padding:.7rem 1rem;
             border-radius:0 8px 8px 0; color:#14532D; font-weight:600; margin:.5rem 0; }
.alerte-2 { background:#FFFBEB; border-left:4px solid #F59E0B; padding:.7rem 1rem;
             border-radius:0 8px 8px 0; color:#78350F; font-weight:600; margin:.5rem 0; }
.alerte-3 { background:#FEF3C7; border-left:4px solid #F97316; padding:.7rem 1rem;
             border-radius:0 8px 8px 0; color:#9A3412; font-weight:600; margin:.5rem 0; }
.alerte-4 { background:#FEE2E2; border-left:4px solid #EF4444; padding:.7rem 1rem;
             border-radius:0 8px 8px 0; color:#7F1D1D; font-weight:700; margin:.5rem 0; }
.tbox { background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:8px; padding:1rem 1.2rem;
        font-family:'Courier New',monospace; font-size:.82rem; line-height:1.7;
        white-space:pre-wrap; color:#1E293B; }
.stButton>button { background:linear-gradient(135deg,#1E3A5F,#2E6DA4)!important;
                   color:white!important; border:none!important; border-radius:8px!important;
                   font-weight:600!important; }
#MainMenu,footer,.stDeployButton { visibility:hidden; }
</style>

“””, unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
st.markdown(”””
<div style="text-align:center;padding:1rem 0;">
<div style="font-size:2.2rem;">🏥</div>
<div style="font-family:'DM Serif Display',serif;font-size:1.3rem;color:#1E3A5F;">INGENIA</div>
<div style="font-size:.75rem;color:#64748B;">Assistant Clinique Intelligent</div>
</div>”””, unsafe_allow_html=True)
st.divider()
page = st.radio(“Navigation”, [“🔍 Analyse”, “📋 Historique”, “📊 Statistiques”],
label_visibility=“collapsed”)
st.divider()
try:
s = stats()
st.caption(f”👤 {s[‘nb_pat’]} patient(s) · 📝 {s[‘nb_obs’]} observation(s)”)
except:
pass
st.markdown(”<div style='font-size:.7rem;color:#94A3B8;margin-top:2rem;text-align:center;'>INGENIA v1.0 · Fabien Barnier · 2026<br>Aide à la réflexion clinique uniquement.</div>”,
unsafe_allow_html=True)

# ── PAGE ANALYSE ──────────────────────────────────────────────────────────────

if “🔍” in page:
st.markdown(”””
<div class="header">
<h1>🏥 INGENIA</h1>
<p>Assistant d’Intelligence Clinique · Aide à la réflexion soignante · Fabien Barnier 2026</p>
</div>”””, unsafe_allow_html=True)

```
with st.container():
    st.markdown('<div class="card"><div class="card-title">👤 Patient</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    nom = c1.text_input("Nom du patient", placeholder="Ex : Mme Dupont Marie", key="nom")
    age = c2.number_input("Âge", 0, 130, 75, key="age")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card"><div class="card-title">📝 Observation Clinique</div>', unsafe_allow_html=True)
obs = st.text_area("Observation", height=110, key="obs", label_visibility="collapsed",
                   placeholder="Exemple : Patient agité cette nuit, refuse de manger, rougeur au sacrum...")
st.markdown("**Exemples rapides :**")
exemples = ["Patient agité cette nuit, refuse de manger",
            "Chute ce matin, rougeur au talon",
            "Confus depuis hier, ne reconnaît plus sa famille",
            "Dyspnée au repos, saturation à 91%"]
cols = st.columns(4)
for i, ex in enumerate(exemples):
    if cols[i].button(f"💬 {i+1}", key=f"ex{i}", use_container_width=True):
        st.session_state["obs"] = ex
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

col_btn, col_save = st.columns([2, 1])
lancer = col_btn.button("🔍 Analyser", use_container_width=True, type="primary")
sauver = col_save.checkbox("💾 Sauvegarder", value=True)

if lancer:
    if not nom.strip():
        st.warning("⚠️ Saisissez le nom du patient.")
    elif not obs.strip():
        st.warning("⚠️ Saisissez une observation.")
    else:
        with st.spinner("🧠 Analyse en cours..."):
            r = analyser(nom, age, obs)
            st.session_state["resultat"] = r
            if sauver:
                try:
                    sauvegarder(nom, age, obs, r["score"], r["transmission"]["texte"])
                except:
                    pass

if "resultat" in st.session_state:
    r = st.session_state["resultat"]
    score = r["score"]
    emojis = {1:"🟢",2:"🟡",3:"🟠",4:"🔴"}

    st.success(f"✅ Analyse terminée — Criticité : {emojis.get(score,'')} Score {score}/4")

    # Alerte
    st.markdown(f'<div class="alerte-{score}">{r["transmission"]["alerte"]}</div>',
                unsafe_allow_html=True)

    # Mots-clés
    if r["mots_cles"]:
        st.markdown('<div class="card"><div class="card-title">🔑 Signes Cliniques Détectés</div>',
                    unsafe_allow_html=True)
        st.markdown(" ".join(f'<span class="tag">{m}</span>' for m in r["mots_cles"]),
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Besoins + Risques
    cb, cr = st.columns(2)
    with cb:
        st.markdown('<div class="card"><div class="card-title">🏥 Besoins Henderson</div>', unsafe_allow_html=True)
        if r["besoins"]:
            for b in r["besoins"]:
                st.markdown(f"**{b['emoji']} {b['label']}**")
        else:
            st.info("Aucun besoin identifié.")
        st.markdown('</div>', unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="card"><div class="card-title">⚠️ Risques Cliniques</div>', unsafe_allow_html=True)
        if r["risques"]:
            for risk in r["risques"]:
                c = "#EF4444" if risk["niveau_urgence"] >= 3 else "#F59E0B"
                st.markdown(f"<span style='color:{c};font-weight:600;'>{risk['emoji']} {risk['label']}</span>",
                            unsafe_allow_html=True)
        else:
            st.info("Aucun risque identifié.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Plan de soins
    if r["plan"]:
        st.markdown('<div class="card"><div class="card-title">📋 Plan de Soins</div>', unsafe_allow_html=True)
        for i, p in enumerate(r["plan"][:8], 1):
            st.markdown(f"**{i}.** {p['action']}  <span style='font-size:.8rem;color:#94A3B8;'>({p['source']})</span>",
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Transmission
    st.markdown('<div class="card"><div class="card-title">📄 Transmission DAR</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="tbox">{r["transmission"]["texte"]}</div>', unsafe_allow_html=True)
    st.download_button("⬇️ Télécharger la transmission",
                       data=r["transmission"]["texte"],
                       file_name=f"transmission_{nom.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                       mime="text/plain")
    st.markdown('</div>', unsafe_allow_html=True)
```

# ── PAGE HISTORIQUE ───────────────────────────────────────────────────────────

elif “📋” in page:
st.markdown(’<div class="header"><h1>📋 Historique Patient</h1><p>Observations enregistrées</p></div>’,
unsafe_allow_html=True)
patients = liste_patients()
if not patients:
st.info(“Aucun patient enregistré. Réalisez d’abord une analyse.”)
else:
choix = st.selectbox(“Choisir un patient”, patients)
if choix:
rows = historique(choix)
st.markdown(f”**{len(rows)} observation(s) pour {choix}**”)
for row in rows:
id_, nom_, age_, obs_, score_, trans_, date_ = row
em = {1:“🟢”,2:“🟡”,3:“🟠”,4:“🔴”}.get(score_,“🟢”)
with st.expander(f”{em} {date_} — Score {score_}/4”):
st.markdown(f”**Observation :** {obs_}”)
if trans_:
st.markdown(f’<div class="tbox">{trans_}</div>’, unsafe_allow_html=True)

# ── PAGE STATISTIQUES ─────────────────────────────────────────────────────────

elif “📊” in page:
st.markdown(’<div class="header"><h1>📊 Statistiques</h1><p>Vue globale de l'activité</p></div>’,
unsafe_allow_html=True)
try:
s = stats()
c1, c2, c3 = st.columns(3)
c1.metric(“👤 Patients”, s[“nb_pat”])
c2.metric(“📝 Observations”, s[“nb_obs”])
c3.metric(“📅 Dernière analyse”, (s[“derniere”] or “—”)[:16])
except Exception as e:
st.error(f”Erreur : {e}”)
