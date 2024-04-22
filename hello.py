import streamlit as st
import sqlite3 
from openai import OpenAI

def init_db():
    with sqlite3.connect('campbellchat.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        row = cursor.fetchone()
        if row is None:
            cursor.execute('''CREATE TABLE users
                    (id integer PRIMARY KEY AUTOINCREMENT, 
                    name text NOT NULL, 
                    assistant text NOT NULL)''')
            conn.commit()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        row = cursor.fetchone()
        if row is None:
            cursor.execute('''CREATE TABLE sessions
                    (id integer PRIMARY KEY AUTOINCREMENT, 
                    user_id integer,
                    name text NOT NULL)''')
            conn.commit()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='session_content'")
        row = cursor.fetchone()
        if row is None:
            cursor.execute('''CREATE TABLE session_content
                    (id integer PRIMARY KEY AUTOINCREMENT, 
                    session_id integer,
                    role TEXT, 
                    content TEXT)''')
            
        conn.commit()

def get_sessions(user_id):
    with sqlite3.connect('campbellchat.db') as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT id, name FROM sessions WHERE user_id = ? ORDER BY id", (user_id,)).fetchall()
        sessions = []
        for row in rows:
            sessions.append({"title": row[1], "session_id": row[0]})
        return sessions

def get_session(session_id):
    with sqlite3.connect('campbellchat.db') as conn:
        cursor = conn.cursor()
        row = cursor.execute("SELECT id, name FROM sessions WHERE id = ? ", (session_id,)).fetchone()
        if row is None:
            return None        
        return {"title": row[1], "session_id": row[0]}

    
def get_session_content(session_id):
    with sqlite3.connect('campbellchat.db') as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT role, content FROM session_content WHERE session_id = ?", (session_id,)).fetchall()
        messages = []
        for row in rows:
            messages.append({"role": row[0], "content": row[1]})
        return messages

def save_message(session_id, role, content):
    with sqlite3.connect('campbellchat.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO session_content(session_id, role, content) VALUES(?,?,?)",(session_id, role, content))
        conn.commit()
    

def create_session(user_id, label):
    with sqlite3.connect('campbellchat.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions(user_id, name) VALUES(?,?)", (user_id, label))
        conn.commit()
        
    return get_session(cursor.lastrowid)

def delete_session(session_id):
    if session_id is not None:
        with sqlite3.connect('campbellchat.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            cursor.execute("DELETE FROM session_content WHERE session_id = ?", (session_id,))
            conn.commit()

def set_current_session_id(session_id):
    st.session_state["current_session_id"] = session_id
    st.session_state.messages = []
    print(f"set the current session : {session_id}")

def get_current_session_id():
    return st.session_state.get("current_session_id")

user_id = 1
st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

init_db()
sessions = get_sessions(user_id=user_id)
print(f"there are { len(sessions)} sessions")

if len(sessions) == 0:
    new_session = create_session(user_id=user_id, label="Ask me anything")
    sessions.append(new_session)
    set_current_session_id(new_session["session_id"])

if get_current_session_id() is None:
    set_current_session_id(sessions[-1]["session_id"])

print(f"the active session is { get_current_session_id()}")

with st.sidebar:
    with st.sidebar.form("new-session"):
        title = st.text_input(label="Start New Session",label_visibility="hidden")
        new_session_btn = st.form_submit_button(label = 'Start new Session 🤖')

    if new_session_btn:         
        if title == "":
            title = "Ask me anything"
        new_session = create_session(user_id=user_id, label=title)
        set_current_session_id(new_session["session_id"])
        sessions.append(new_session)

    for session in sessions:
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            st.write(session["title"])
        
        with col2:
            if st.button(label="➡️", key=f"sb-g-{session['session_id']}"):
                set_current_session_id(session['session_id'])
        with col3:
            if st.button(label="❌", key=f"sb-d-{session['session_id']}"):
                print(f"delete {session['title']}")
                delete_session(session['session_id'])
                sessions[:] = [session for s in sessions if s["session_id"] != session['session_id']]        
                set_current_session_id(None)
                st.rerun()

st.write("# Welcome to CampbellChat 🥫")

title = "Ask me anything"
for s in sessions:
    if s["session_id"] == get_current_session_id():
        title = s["title"]
        break

st.write(f"## { title }")

st.session_state["openai_model"] = st.secrets["OLLAMA_MODEL"]
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url=st.secrets["OLLAMA_BASE_URL"])
content = get_session_content(get_current_session_id())
for message in content:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.session_state.messages = content

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(get_current_session_id(), "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    save_message(get_current_session_id(), "assistant", response)