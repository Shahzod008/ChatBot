from requests.auth import HTTPBasicAuth
import streamlit as st
import requests
import json
import uuid

st.title("Чат бот")


if "access_token" not in st.session_state:
    try:
        st.session_state.access_token = requests.post(
            url="https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": str(uuid.uuid4())
            },
            auth=HTTPBasicAuth(st.secrets["CLIENT_ID"], st.secrets["SECRET"]),
            data={"scope": "GIGACHAT_API_PERS"},
            verify=False
        ).json()["access_token"]
        st.toast("Бот полностью готов отвечать на ваши вопросы")
    except Exception as e:
        st.toast(f"Не получилось получить токен {e}")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "ai",
            "content": "Чем могу помочь?"
        }
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if user_prompt := st.chat_input():
    res = requests.post(
        url="https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {st.session_state.access_token}'
        },
        data=json.dumps(
            {
                "model": "GigaChat",
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            }
        ),
        verify=False
    ).json()["choices"][0]["message"]["content"]

    st.chat_message("user").write(user_prompt)
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    with st.spinner("В процессе..."):
        st.chat_message("ai").write(
            res
        )
        st.session_state.messages.append(
            {
                "role": "ai",
                "content": res
            }
        )
