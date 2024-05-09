# Campbell Chat

This is an experiment on how to build applications using local models using Streamlit and [Ollama](https://ollama.com)

This is my attempt to a barebones ChatGPT clone.  This uses Ollama and Llama3 but it should technically work with any model and OpenAI-compatible API.


## Prerequisites
1. Install ollama in your machine and start it
2. Pull the llama3 model (`ollama pull llama3`)
3. Python 3

## How to Use

1. At the root of this repo, create a folder called `.streamlit` and inside it create file called `secrets.toml` with the following content (you can change the values if you want to use a different model or the OpenAI service)

        OPENAI_API_KEY = "ollama"
        OLLAMA_BASE_URL= "http://localhost:11434/v1"
        OLLAMA_MODEL ="llama3"

2. Crete a virtual environment, activate it,  and install the dependencies

        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt

3. Start the streamlit service

        streamlit run hello.py

4. Go to `http://localhost:8501/` and start chatting!
