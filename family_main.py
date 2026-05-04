# -*- coding: utf-8 -*-
import streamlit as st
import requests
import os
import json
import hashlib
import time
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# ---------- КОНФИГУРАЦИЯ ----------
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "gemma4:e4b"

APPDATA_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'FamilyMentor')
os.makedirs(APPDATA_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(APPDATA_DIR, "family_config.json")
HISTORY_FILE = os.path.join(APPDATA_DIR, "chat_history.json")
LOGS_FILE = os.path.join(APPDATA_DIR, "family_logs.json")

# ======================= ДВУЯЗЫЧНЫЕ ТЕКСТЫ =======================
TEXTS = {
    "ru": {
        "app_title": "Семейный Наставник",
        "app_subtitle": "Твой добрый и умный помощник",
        "mentor_badge": "Наставник:",
        "settings": "⚙️ Настройки",
        "profile": "👤 Твой профиль",
        "name_label": "Имя",
        "gender_label": "Пол",
        "male": "мальчик",
        "female": "девочка",
        "save": "Сохранить",
        "change_mentor": "Сменить наставника",
        "apply": "Применить",
        "facts": "Показывать факты",
        "facts_topic": "Тема фактов",
        "clear_chat": "Очистить чат",
        "free_mode": "🔓 Свободный режим",
        "parent_control": "🔒 Родительский контроль",
        "parent_password": "Пароль родителя",
        "repeat_password": "Повторите пароль",
        "daily_limit": "Дневной лимит (минут)",
        "activate": "Активировать",
        "parent_panel": "Родительская панель",
        "new_limit": "Новый лимит (минут)",
        "update_limit": "Обновить лимит",
        "revoke_consent": "Отозвать согласие",
        "close_panel": "Закрыть панель",
        "exit": "Выйти",
        "ask_question": "Напиши свой вопрос...",
        "button_answer_received": "✅ Ответ получен",
        "thinking": "Наставник думает...",
        "limit_exceeded": "⏰ Дневной лимит исчерпан.",
        "remaining_time": "Осталось минут",
        "error_server": "⚠️ Сервер Ollama не отвечает. Запустите 'ollama serve' вручную.",
        "error_model": "⚠️ Ошибка модели",
        "attribution": "Gemma is a trademark of Google LLC.",
        "model_based": "Модель gemma4:e4b основана на Gemma 4.",
        "welcome_launcher": "🧸 Добро пожаловать в клуб **«Семейный Наставник»**",
        "consent_title": "📜 Пользовательское соглашение",
        "consent_text": """
**Согласие на обработку персональных данных**  
Вы даёте согласие на локальную обработку имени, пола, истории чата, времени использования.  
Все данные хранятся только на вашем устройстве, не передаются третьим лицам.

**Устанавливаемое ПО**  
- Ollama (сервер AI)  
- Модель Gemma 4 (gemma4:e4b) – загружается один раз (около 9.6 ГБ)

**Системные требования**  
Windows 10/11, 8 ГБ ОЗУ (рекомендуется 16 ГБ), 6 ГБ свободного места, интернет для загрузки модели.

**Инструкция**  
- При первом запуске может потребоваться установка Ollama и загрузка модели (10–30 минут).  
- Не закрывайте окно принудительно.  
- После завершения нажмите «Запустить приложение».

Нажимая «Принимаю», вы подтверждаете согласие.
        """,
        "install_warning": "⚠️ Первая установка может занять 10–30 минут. Не закрывайте окно.",
        "install_button": "✅ Принимаю и продолжить",
        "install_ollama": "📦 Установка Ollama...",
        "downloading_model": "🔄 Загрузка модели gemma4:e4b (около 9.6 ГБ). Займёт 10–30 минут...",
        "setup_success": "✅ Готово! Теперь можно запустить приложение.",
        "launch_button": "🚀 Запустить Семейный Наставник",
        "rules_intro": (
            "🧸 **Уважаемый пользователь!**\n\n"
            "Ознакомься, пожалуйста, с правилами общения с Наставником:\n"
            "1. Если вопрос слишком общий, я попрошу уточнить – просто напиши детали.\n"
            "2. После ответа я спрошу: «Ты добился того, чего хотел?» – если да, нажми кнопку **«✅ Ответ получен»** внизу. Если нет – напиши, чем ещё помочь.\n"
            "3. Ты можешь очистить чат в любой момент через боковое меню.\n\n"
            "А теперь задавай свой вопрос!"
        )
    },
    "en": {
        "app_title": "Family Mentor",
        "app_subtitle": "Your kind and smart assistant",
        "mentor_badge": "Mentor:",
        "settings": "⚙️ Settings",
        "profile": "👤 Your profile",
        "name_label": "Name",
        "gender_label": "Gender",
        "male": "boy",
        "female": "girl",
        "save": "Save",
        "change_mentor": "Change mentor",
        "apply": "Apply",
        "facts": "Show facts",
        "facts_topic": "Facts topic",
        "clear_chat": "Clear chat",
        "free_mode": "🔓 Free mode",
        "parent_control": "🔒 Parental control",
        "parent_password": "Parent password",
        "repeat_password": "Repeat password",
        "daily_limit": "Daily limit (minutes)",
        "activate": "Activate",
        "parent_panel": "Parent panel",
        "new_limit": "New limit (minutes)",
        "update_limit": "Update limit",
        "revoke_consent": "Revoke consent",
        "close_panel": "Close panel",
        "exit": "Exit",
        "ask_question": "Write your question...",
        "button_answer_received": "✅ Answer received",
        "thinking": "Mentor is thinking...",
        "limit_exceeded": "⏰ Daily limit exceeded.",
        "remaining_time": "Minutes left",
        "error_server": "⚠️ Ollama server is not responding. Run 'ollama serve' manually.",
        "error_model": "⚠️ Model error",
        "attribution": "Gemma is a trademark of Google LLC.",
        "model_based": "Model gemma4:e4b is based on Gemma 4.",
        "welcome_launcher": "🧸 Welcome to the **Family Mentor** club",
        "consent_title": "📜 User agreement",
        "consent_text": """
**Consent to personal data processing**  
You agree to the local processing of name, gender, chat history, usage time.  
All data is stored only on your device and is not shared with third parties.

**Software to be installed**  
- Ollama (AI server)  
- Gemma 4 model (gemma4:e4b) – downloaded once (approx. 9.6 GB)

**System requirements**  
Windows 10/11, 8 GB RAM (16 GB recommended), 6 GB free space, internet for model download.

**Instructions**  
- First launch may require Ollama installation and model download (10–30 minutes).  
- Do not forcibly close the window.  
- After completion click "Launch the application".

By clicking "I accept", you confirm your consent.
        """,
        "install_warning": "⚠️ First installation may take 10–30 minutes. Do not close the window.",
        "install_button": "✅ I accept and proceed",
        "install_ollama": "📦 Installing Ollama...",
        "downloading_model": "🔄 Downloading gemma4:e4b model (approx. 9.6 GB). Will take 10–30 minutes...",
        "setup_success": "✅ Done! Now you can launch the application.",
        "launch_button": "🚀 Launch Family Mentor",
        "rules_intro": (
            "🧸 **Dear user!**\n\n"
            "Please read the rules for communicating with the Mentor:\n"
            "1. If the question is too broad, I will ask for clarification – just write the details.\n"
            "2. After an answer, I will ask: 'Did you achieve what you wanted?' – if yes, press the **«✅ Answer received»** button below. If not, write how I can help further.\n"
            "3. You can clear the chat at any time via the sidebar.\n\n"
            "Now ask your question!"
        )
    }
}

# ======================= ДВУЯЗЫЧНЫЕ ПРОМПТЫ НАСТАВНИКОВ (ПОЛНЫЕ) =======================
SYSTEM_PROMPTS = {
    "ru": {
        "Кибер": """Ты — Наставник КИБЕР, добрый, умный и весёлый эксперт по всем темам в мире. Ты общаешься с детьми и подростками 7–14 лет. Говори простым, понятным языком, используй «ты», умеренно эмодзи, не шути много, будь всегда вежливым. Поддерживай и поощряй стремления пользователя к знаниям.

Правила диалога:
1. Если вопрос слишком общий (например, «расскажи о себе»), НЕ повторяй одну просьбу уточнить дважды. Сначала вежливо попроси уточнить: «Это очень широкий вопрос. Уточни, пожалуйста, детали — что именно тебя интересует? Например: мои возможности, моя история или как я могу помочь?». Затем жди уточнения (система переведёт в режим ожидания).
2. После того как пользователь дал уточнение, дай развёрнутый, интересный ответ, добавь интересный факт (если уместно).
3. После ответа спроси пользователя: «Ты добился того, чего хотел? Если да – нажми кнопку «✅ Ответ получен». Если нет – напиши, чем ещё помочь».
4. Если пользователь продолжает писать текст, продолжай помогать, затем снова спроси о достижении цели.
5. Всегда обращайся к пользователю по имени ({name}), учитывай его пол ({gender_word}). Твой тон — добрый, терпеливый, как у лучшего друга.

Пример для «расскажи о себе»:
- Без уточнений: «Это широкий вопрос. Тебя интересуют мои способности, как я устроен или как я могу помочь в учёбе? Уточни, пожалуйста.»
- После уточнения дай конкретный ответ о своих возможностях как наставника.""",
        "Солнечный": """Ты — Наставник СОЛНЕЧНЫЙ, добрый, умный эксперт по всем темам в мире. ... (полностью те же правила, что и для Кибера) ...""",
        "Мудрец": """Ты — Наставник МУДРЕЦ, очень умный, заботливый, добрый, но в меру строгий эксперт. ... (полностью те же правила, что и для Кибера) ..."""
    },
    "en": {
        "Кибер": """You are MENTOR CYBER, a kind, smart, and cheerful expert on all topics. You talk to children aged 7–14. Use simple language, 'you', moderate emojis, be polite.

Dialogue rules:
1. If the user asks a very broad question (e.g., "tell me about yourself"), do NOT repeat the same clarification request twice. First, politely ask: "That's a broad question. Could you please clarify what exactly interests you? For example: your abilities, your origin, or how you help?". Then wait for clarification (the system will set awaiting_clarification flag).
2. After the user clarifies, give a detailed, interesting answer, add a fun fact if appropriate.
3. After answering, ask: "Did you achieve what you wanted? If yes – press the '✅ Answer received' button. If not – write how I can help further."
4. If the user continues writing, keep helping, then ask again about achieving the goal.
5. Always address the user by name ({name}) and consider their gender ({gender_word}). Be kind and patient like a best friend.

Example for "tell me about yourself":
- Without details: "That's a broad question. Would you like to know about my abilities, how I was created, or how I can help you learn? Please clarify."
- After clarification: give a specific answer about your capabilities as a mentor.""",
        "Солнечный": """You are MENTOR SUNNY, a kind, smart expert on all topics. ... (same rules as for Cyber) ...""",
        "Мудрец": """You are MENTOR SAGE, a wise, caring, kind but moderately strict expert. ... (same rules as for Cyber) ..."""
    }
}

WELCOME_MESSAGES = {
    "ru": {
        "Кибер": "Привет! 👋 Я Кибер. Что тебя интересует?",
        "Солнечный": "Привет! 👋 Я СОЛНЫШКО. Что тебя интересует?",
        "Мудрец": "Здравствуй! 👋 Я Мудрец. Задавай вопрос."
    },
    "en": {
        "Кибер": "Hi! 👋 I'm Cyber. What interests you?",
        "Солнечный": "Hi! 👋 I'm SUNNY. What interests you?",
        "Мудрец": "Hello! 👋 I'm Sage. Ask your question."
    }
}

FACTS_DB = {
    "Космос": ["🚀 Один день на Венере длиннее года!", "🌕 На Луне есть горы выше Эвереста.", "🪐 Сатурн мог бы плавать в воде."],
    "Животные": ["🐙 У осьминога три сердца.", "🦒 Жирафы спят 30 минут в день."],
    "Наука": ["🧪 Вода может кипеть и замерзать одновременно.", "⚡ Молния нагревает воздух до 30 000 °C."],
}

# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------
def get_image_path(filename):
    p = Path(__file__).parent / "assets" / filename
    return str(p) if p.exists() else None

logo_ico = get_image_path("logo.ico")
if logo_ico:
    st.set_page_config(page_title="Family Mentor", page_icon=logo_ico, layout="wide")
else:
    st.set_page_config(page_title="Family Mentor", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;600&display=swap');
body { font-family: 'Comfortaa', sans-serif; }
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
h1, h2, h3 { color: #ffffff !important; font-weight: 600; }
div[data-testid="stChatMessage"][data-role="user"] { background-color: #4facfe !important; color: white; border-radius: 18px; padding: 14px 18px; margin-left: 15%; margin-right: 0; }
div[data-testid="stChatMessage"][data-role="assistant"] { background-color: #ffffff !important; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-radius: 18px; padding: 14px 18px; margin-right: 15%; margin-left: 0; }
@media (max-width: 992px) { div[data-testid="stChatMessage"][data-role="user"], div[data-testid="stChatMessage"][data-role="assistant"] { margin-left: 5%; margin-right: 5%; } }
@media (max-width: 768px) { div[data-testid="stChatMessage"][data-role="user"], div[data-testid="stChatMessage"][data-role="assistant"] { margin-left: 2%; margin-right: 2%; border-radius: 16px; padding: 10px 14px; } h1 { font-size: 1.8rem !important; } }
.stButton > button { border-radius: 25px; background: linear-gradient(145deg, #f093fb 0%, #f5576c 100%); color: white; border: none; font-weight: 600; width: 100%; }
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 7px 14px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return default if default is not None else {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_system_prompt(mentor, name, gender_word, lang):
    if mentor not in SYSTEM_PROMPTS[lang]:
        mentor = "Кибер"
    return SYSTEM_PROMPTS[lang][mentor].format(name=name, gender_word=gender_word)

def get_welcome_message(mentor, lang):
    return WELCOME_MESSAGES[lang].get(mentor, WELCOME_MESSAGES[lang]["Кибер"])

def get_rules_message(lang):
    return TEXTS[lang]["rules_intro"]

def log_event(event_type, details=""):
    logs = load_json(LOGS_FILE, [])
    logs.append({"timestamp": datetime.now().isoformat(), "type": event_type, "details": details})
    save_json(LOGS_FILE, logs)

def get_today_usage_minutes():
    logs = load_json(LOGS_FILE, [])
    today = datetime.now().date()
    questions = []
    for e in logs:
        if e["type"] == "question":
            try:
                ts = datetime.fromisoformat(e["timestamp"])
                if ts.date() == today:
                    questions.append(ts)
            except:
                continue
    if len(questions) <= 1:
        return 0
    questions.sort()
    total_seconds = 0
    for i in range(1, len(questions)):
        delta = (questions[i] - questions[i-1]).total_seconds()
        if delta > 900:
            delta = 900
        total_seconds += delta
    return int(total_seconds // 60)

def init_session_state():
    config = load_json(CONFIG_FILE, {})
    if "messages" not in st.session_state:
        hist = load_json(HISTORY_FILE, [])
        if hist:
            st.session_state.messages = hist
        else:
            lang = config.get("language", "ru")
            mentor = st.session_state.get("selected_mentor", "Кибер")
            rules = get_rules_message(lang)
            welcome = get_welcome_message(mentor, lang)
            st.session_state.messages = [
                {"role": "assistant", "content": rules},
                {"role": "assistant", "content": welcome}
            ]

    defaults = {
        "selected_mentor": "Кибер",
        "daily_limit": config.get("daily_limit", 999),
        "facts_enabled": True,
        "facts_topic": config.get("facts_topic", "Космос"),
        "facts_index": 0,
        "last_fact_update": datetime.now(),
        "parent_control_active": config.get("parent_control_active", False),
        "parent_verified": False,
        "show_parent_setup": False,
        "last_activity_time": datetime.now(),
        "session_open": False,
        "awaiting_clarification": False,
        "awaiting_satisfaction": False,
        "consent_given": config.get("consent_given", False),
        "setup_completed": config.get("setup_completed", False),
        "language": config.get("language", "ru"),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    st.session_state.daily_limit = config.get("daily_limit", 999)

def call_ollama(messages):
    lang = st.session_state.language
    try:
        requests.get("http://localhost:11434/api/tags", timeout=1)
    except:
        subprocess.run("taskkill /F /IM ollama.exe >nul 2>&1", shell=True)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen(["ollama", "serve"], shell=True, startupinfo=startupinfo)
        time.sleep(5)
        try:
            requests.get("http://localhost:11434/api/tags", timeout=2)
        except:
            return TEXTS[lang]["error_server"]
    config = load_json(CONFIG_FILE, {})
    name = config.get("child_name", "Гость" if lang == "ru" else "Guest")
    gender = config.get("user_gender", "мальчик" if lang == "ru" else "boy")
    gender_word = "мальчик" if gender == "мальчик" else "девочка" if lang == "ru" else "boy" if gender == "boy" else "girl"
    mentor = st.session_state.selected_mentor
    system_prompt = get_system_prompt(mentor, name, gender_word, lang)
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    try:
        r = requests.post(f"http://localhost:11434/api/chat", json={
            "model": "gemma4:e4b",
            "messages": full_messages,
            "stream": False
        }, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"]
    except Exception as e:
        return f"{TEXTS[lang]['error_model']}: {e}"

# ---------- ОБРАБОТКА ВВОДА ----------
def process_user_input(user_input):
    lang = st.session_state.language

    # Режим ожидания уточнения (широкий вопрос)
    if st.session_state.awaiting_clarification:
        # Защита от повторного широкого вопроса
        broad_phrases = ["tell me about yourself", "about yourself", "расскажи о себе", "what can you do", "who are you"]
        if any(phrase in user_input.lower() for phrase in broad_phrases):
            specific_answer = "I am your Family Mentor, created to help children learn. I can answer questions about space, animals, science, and more. How can I assist you today? (Если хочешь на русском, спроси по-русски)."
            if lang == "ru":
                specific_answer = "Я твой Семейный Наставник, созданный, чтобы помогать детям учиться. Я могу отвечать на вопросы о космосе, животных, науке и многом другом. Чем я могу помочь тебе сегодня?"
            st.session_state.messages.append({"role": "assistant", "content": specific_answer})
            st.session_state.awaiting_clarification = False
            st.session_state.awaiting_satisfaction = True
            satisfaction_msg = "Did you achieve what you wanted? If yes – press '✅ Answer received'. If not – write how I can help further."
            if lang == "ru":
                satisfaction_msg = "Ты добился того, чего хотел? Если да – нажми кнопку «✅ Ответ получен». Если нет – напиши, чем ещё помочь."
            st.session_state.messages.append({"role": "assistant", "content": satisfaction_msg})
            save_json(HISTORY_FILE, st.session_state.messages)
            st.rerun()
            return
        # Обычная обработка уточнения
        st.session_state.awaiting_clarification = False
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner(TEXTS[lang]["thinking"]):
            answer = call_ollama(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.awaiting_satisfaction = True
        satisfaction_msg = "Did you achieve what you wanted? If yes – press '✅ Answer received'. If not – write how I can help further."
        if lang == "ru":
            satisfaction_msg = "Ты добился того, чего хотел? Если да – нажми кнопку «✅ Ответ получен». Если нет – напиши, чем ещё помочь."
        st.session_state.messages.append({"role": "assistant", "content": satisfaction_msg})
        save_json(HISTORY_FILE, st.session_state.messages)
        st.rerun()
        return

    # Режим ожидания ответа на "Ты добился?" (пользователь пишет текст)
    if st.session_state.awaiting_satisfaction:
        st.session_state.awaiting_satisfaction = False
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner(TEXTS[lang]["thinking"]):
            answer = call_ollama(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.awaiting_satisfaction = True
        satisfaction_msg = "Did you achieve what you wanted? If yes – press '✅ Answer received'. If not – write how I can help further."
        if lang == "ru":
            satisfaction_msg = "Ты добился того, чего хотел? Если да – нажми кнопку «✅ Ответ получен». Если нет – напиши, чем ещё помочь."
        st.session_state.messages.append({"role": "assistant", "content": satisfaction_msg})
        save_json(HISTORY_FILE, st.session_state.messages)
        st.rerun()
        return

    # Обычный режим: новый вопрос (сессия не открыта)
    if not st.session_state.session_open:
        st.session_state.session_open = True
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner(TEXTS[lang]["thinking"]):
            answer = call_ollama(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        # Определяем, широкий ли вопрос (по ключевым фразам в ответе)
        if any(phrase in answer.lower() for phrase in ["уточни", "детали", "широкий", "несколько страниц", "clarify", "details", "broad"]):
            st.session_state.awaiting_clarification = True
        else:
            st.session_state.awaiting_satisfaction = True
            satisfaction_msg = "Did you achieve what you wanted? If yes – press '✅ Answer received'. If not – write how I can help further."
            if lang == "ru":
                satisfaction_msg = "Ты добился того, чего хотел? Если да – нажми кнопку «✅ Ответ получен». Если нет – напиши, чем ещё помочь."
            st.session_state.messages.append({"role": "assistant", "content": satisfaction_msg})
        save_json(HISTORY_FILE, st.session_state.messages)
        st.rerun()
        return

    # Запасной вариант (если сессия открыта, но нет режимов – например, ошибка)
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner(TEXTS[lang]["thinking"]):
        answer = call_ollama(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    save_json(HISTORY_FILE, st.session_state.messages)
    st.rerun()

def close_session():
    lang = st.session_state.language
    if st.session_state.session_open:
        st.session_state.session_open = False
        st.session_state.awaiting_clarification = False
        st.session_state.awaiting_satisfaction = False
        if lang == "ru":
            msg = "🔒 Сессия закрыта. Если захочешь задать новый вопрос, просто напиши его. Что тебя интересует?"
        else:
            msg = "🔒 Session closed. If you want to ask a new question, just write it. What interests you?"
        st.session_state.messages.append({"role": "assistant", "content": msg})
        save_json(HISTORY_FILE, st.session_state.messages)
        st.rerun()

# ---------- ЛАУНЧЕР ----------
def show_launcher():
    config = load_json(CONFIG_FILE, {})
    current_lang = config.get("language", "ru")

    st.markdown("### 🌐 Language / Язык")
    new_lang = st.radio(
        "",
        ["ru", "en"],
        index=0 if current_lang == "ru" else 1,
        format_func=lambda x: "🇷🇺 Русский" if x == "ru" else "🇬🇧 English",
        horizontal=True,
        key="lang_radio_launcher"
    )
    if new_lang != current_lang:
        config["language"] = new_lang
        save_json(CONFIG_FILE, config)
        st.session_state.language = new_lang
        for key in list(st.session_state.keys()):
            if key not in ["consent_given", "setup_completed", "language"]:
                del st.session_state[key]
        st.rerun()
    lang = new_lang

    st.markdown(f"## {TEXTS[lang]['welcome_launcher']}")
    with st.expander(TEXTS[lang]["consent_title"], expanded=True):
        st.markdown(TEXTS[lang]["consent_text"])
    st.warning(TEXTS[lang]["install_warning"])

    if st.button(TEXTS[lang]["install_button"], use_container_width=True):
        config = load_json(CONFIG_FILE, {})
        config["consent_given"] = True
        config["language"] = lang
        save_json(CONFIG_FILE, config)
        st.session_state.consent_given = True
        st.session_state.language = lang
        st.session_state.setup_completed = False

        with st.spinner(" "):
            if not shutil.which("ollama"):
                st.info(TEXTS[lang]["install_ollama"])
                subprocess.run(["powershell", "-Command", "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe'"], shell=True)
                subprocess.run(["OllamaSetup.exe", "/S"], shell=True)
                time.sleep(5)

            subprocess.run("taskkill /F /IM ollama.exe >nul 2>&1", shell=True)
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(["ollama", "serve"], shell=True, startupinfo=startupinfo)
            for _ in range(20):
                time.sleep(1)
                try:
                    if requests.get("http://localhost:11434/api/tags", timeout=1).status_code == 200:
                        break
                except:
                    pass

            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, shell=True)
            if "gemma4:e4b" not in result.stdout:
                st.info(TEXTS[lang]["downloading_model"])
                subprocess.run(["ollama", "pull", "gemma4:e4b"], shell=True)

            config["setup_completed"] = True
            save_json(CONFIG_FILE, config)
            st.session_state.setup_completed = True
            st.success(TEXTS[lang]["setup_success"])
            if st.button(TEXTS[lang]["launch_button"]):
                st.rerun()

# ---------- ОСНОВНОЙ ИНТЕРФЕЙС ----------
def main_interface():
    init_session_state()
    config = load_json(CONFIG_FILE, {})
    lang = st.session_state.language

    logo_img = get_image_path("logo.png")
    if logo_img:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image(logo_img, width=200)

    st.markdown(f'<h1 style="text-align: center;">{TEXTS[lang]["app_title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #ddd;">{TEXTS[lang]["app_subtitle"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<div style="display: inline-block; padding: 9px 24px; background: rgba(255,255,255,0.2); border-radius: 30px; color: white; font-weight: 600;">{TEXTS[lang]["mentor_badge"]} {st.session_state.selected_mentor}</div>', unsafe_allow_html=True)

    with st.sidebar:
        logus = get_image_path("logus.ico")
        if logus:
            st.image(logus, width=64)

        new_lang = st.radio("Language", ["ru", "en"], index=0 if lang=="ru" else 1,
                            format_func=lambda x: "🇷🇺 Русский" if x=="ru" else "🇬🇧 English", horizontal=True, key="lang_radio_sidebar")
        if new_lang != lang:
            config["language"] = new_lang
            save_json(CONFIG_FILE, config)
            st.session_state.language = new_lang
            st.rerun()

        st.header(TEXTS[lang]["settings"])
        with st.expander(TEXTS[lang]["profile"]):
            new_name = st.text_input(TEXTS[lang]["name_label"], value=config.get("child_name", "Гость" if lang=="ru" else "Guest"))
            new_gender = st.radio(TEXTS[lang]["gender_label"], [TEXTS[lang]["male"], TEXTS[lang]["female"]],
                                  index=0 if config.get("user_gender")==TEXTS[lang]["male"] else 1)
            if st.button(TEXTS[lang]["save"]):
                config["child_name"] = new_name
                config["user_gender"] = new_gender
                save_json(CONFIG_FILE, config)
                st.rerun()

        new_mentor = st.selectbox(TEXTS[lang]["change_mentor"], list(SYSTEM_PROMPTS[lang].keys()),
                                  index=list(SYSTEM_PROMPTS[lang].keys()).index(st.session_state.selected_mentor))
        if st.button(TEXTS[lang]["apply"]):
            if new_mentor != st.session_state.selected_mentor:
                st.session_state.selected_mentor = new_mentor
                rules = get_rules_message(lang)
                welcome = get_welcome_message(new_mentor, lang)
                st.session_state.messages = [
                    {"role": "assistant", "content": rules},
                    {"role": "assistant", "content": welcome}
                ]
                st.session_state.session_open = False
                st.session_state.awaiting_clarification = False
                st.session_state.awaiting_satisfaction = False
                save_json(HISTORY_FILE, st.session_state.messages)
                st.rerun()

        st.session_state.facts_enabled = st.checkbox(TEXTS[lang]["facts"], st.session_state.facts_enabled)
        if st.session_state.facts_enabled:
            new_topic = st.selectbox(TEXTS[lang]["facts_topic"], list(FACTS_DB.keys()),
                                     index=list(FACTS_DB.keys()).index(st.session_state.facts_topic))
            if new_topic != st.session_state.facts_topic:
                st.session_state.facts_topic = new_topic
                config["facts_topic"] = new_topic
                save_json(CONFIG_FILE, config)

        if st.button(TEXTS[lang]["clear_chat"]):
            rules = get_rules_message(lang)
            welcome = get_welcome_message(st.session_state.selected_mentor, lang)
            st.session_state.messages = [
                {"role": "assistant", "content": rules},
                {"role": "assistant", "content": welcome}
            ]
            st.session_state.session_open = False
            st.session_state.awaiting_clarification = False
            st.session_state.awaiting_satisfaction = False
            save_json(HISTORY_FILE, [])
            st.rerun()

        st.markdown("---")
        if not st.session_state.parent_control_active:
            st.info(TEXTS[lang]["free_mode"])
            if st.button(TEXTS[lang]["parent_control"]):
                st.session_state.show_parent_setup = True
            if st.session_state.show_parent_setup:
                with st.form("parent_setup_form"):
                    st.subheader(TEXTS[lang]["parent_control"])
                    parent_password = st.text_input(TEXTS[lang]["parent_password"], type="password")
                    parent_password2 = st.text_input(TEXTS[lang]["repeat_password"], type="password")
                    daily_limit = st.number_input(TEXTS[lang]["daily_limit"], min_value=10, value=60)
                    submitted = st.form_submit_button(TEXTS[lang]["activate"])
                    if submitted:
                        if parent_password and parent_password == parent_password2:
                            config["parent_password_hash"] = hashlib.sha256(parent_password.encode()).hexdigest()
                            config["daily_limit"] = daily_limit
                            config["parent_control_active"] = True
                            save_json(CONFIG_FILE, config)
                            st.session_state.parent_control_active = True
                            st.session_state.daily_limit = daily_limit
                            st.session_state.show_parent_setup = False
                            st.rerun()
                        else:
                            st.error("Пароли не совпадают" if lang=="ru" else "Passwords do not match")
        else:
            st.success(TEXTS[lang]["parent_control"])
            used = get_today_usage_minutes()
            limit = st.session_state.daily_limit
            remaining = max(limit - used, 0)
            st.metric(TEXTS[lang]["remaining_time"], f"{remaining} / {limit}")
            if remaining <= 0:
                st.error(TEXTS[lang]["limit_exceeded"])

            if not st.session_state.parent_verified:
                with st.form("parent_login"):
                    pwd = st.text_input(TEXTS[lang]["parent_password"], type="password")
                    if st.form_submit_button(TEXTS[lang]["activate"]):
                        if hashlib.sha256(pwd.encode()).hexdigest() == config.get("parent_password_hash", ""):
                            st.session_state.parent_verified = True
                            st.rerun()
                        else:
                            st.error("Неверный пароль" if lang=="ru" else "Wrong password")
            else:
                st.subheader(TEXTS[lang]["parent_panel"])
                if os.path.exists(LOGS_FILE):
                    with open(LOGS_FILE, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                    if logs:
                        import pandas as pd
                        st.dataframe(pd.DataFrame(logs))
                new_limit = st.number_input(TEXTS[lang]["new_limit"], value=config.get("daily_limit", 60))
                if st.button(TEXTS[lang]["update_limit"]):
                    config["daily_limit"] = new_limit
                    save_json(CONFIG_FILE, config)
                    st.session_state.daily_limit = new_limit
                    st.rerun()
                if st.button(TEXTS[lang]["revoke_consent"]):
                    config["consent_given"] = False
                    config["setup_completed"] = False
                    save_json(CONFIG_FILE, config)
                    st.session_state.consent_given = False
                    st.session_state.setup_completed = False
                    st.rerun()
                if st.button(TEXTS[lang]["close_panel"]):
                    st.session_state.parent_verified = False
                    st.rerun()

        st.markdown("---")
        st.caption(TEXTS[lang]["attribution"])
        st.caption(TEXTS[lang]["model_based"])
        if st.button(TEXTS[lang]["exit"]):
            save_json(HISTORY_FILE, st.session_state.messages)
            st.stop()

    # Факты
    if st.session_state.facts_enabled:
        now = datetime.now()
        if (now - st.session_state.last_fact_update).total_seconds() > 12:
            facts = FACTS_DB[st.session_state.facts_topic]
            st.session_state.facts_index = (st.session_state.facts_index + 1) % len(facts)
            st.session_state.last_fact_update = now
        fact = FACTS_DB[st.session_state.facts_topic][st.session_state.facts_index]
        st.markdown(f"📢 **{TEXTS[lang]['facts_topic']}:** {fact}")

    if st.session_state.parent_control_active:
        used = get_today_usage_minutes()
        if used >= st.session_state.daily_limit:
            st.error(TEXTS[lang]["limit_exceeded"])
            st.stop()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.chat_input(TEXTS[lang]["ask_question"])
    with col2:
        if st.button(TEXTS[lang]["button_answer_received"], use_container_width=True):
            close_session()

    if user_input:
        log_event("question", f"user_input={user_input}")
        process_user_input(user_input)
        st.rerun()

# ---------- ТОЧКА ВХОДА ----------
if __name__ == "__main__":
    config = load_json(CONFIG_FILE, {})
    if not config.get("consent_given", False):
        show_launcher()
    else:
        if not config.get("setup_completed", False):
            with st.spinner(" "):
                if not shutil.which("ollama"):
                    lang = config.get("language", "ru")
                    st.error(TEXTS[lang]["error_server"] + " (Ollama not installed)")
                    st.stop()
                subprocess.run("taskkill /F /IM ollama.exe >nul 2>&1", shell=True)
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.Popen(["ollama", "serve"], shell=True, startupinfo=startupinfo)
                time.sleep(5)
                result = subprocess.run(["ollama", "list"], capture_output=True, text=True, shell=True)
                if "gemma4:e4b" not in result.stdout:
                    lang = config.get("language", "ru")
                    st.error(TEXTS[lang]["error_model"] + " (gemma4:e4b not found)")
                    st.stop()
                config["setup_completed"] = True
                save_json(CONFIG_FILE, config)
                lang = config.get("language", "ru")
                st.success(TEXTS[lang]["setup_success"] if lang=="ru" else "Ready! Please restart the application.")
                time.sleep(2)
                st.rerun()
        else:
            main_interface()