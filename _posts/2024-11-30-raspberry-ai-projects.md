---
title: AI Projects on a Raspberry Pi
author: JAlcocerT
date: 2024-11-30
categories: [Make your Raspberry Useful]
tags: [AI]
mermaid: true
---

These year the Pi5 was launched.

What a perfect oportunity that was to get finally a **Raspbery Pi 4 with a reasonable price** and do some **AI projects with it**.

This time I got a 4GB Pi4, ARM64!

Let's do some cool stuff with it.

- [ ] Raspberry Pi can do more than IoT. **Go AI with a RPi**
  + [x] [Python](#faq) Checks 👇
  + [ ] [Docker](#faq) Checks
  + [ ] Third Party APIs: OpenAI, Anthropic, Groq, also Ollama!
  + [ ] [Use AI Tools](#ai-stack) with your Raspberry Pi  

| Project             | Code                  | Use Case |
|---------------------|:---------------------:|:-----------:|
| `Streamlit Multi-Chat`  ✓  | [Source Code](https://github.com/JAlcocerT/Streamlit-MultiChat)  🐍 [Container](https://github.com/JAlcocerT/phidata/pkgs/container/phidata)      | Chat with Several LLMs (APIs). See [Blog](https://jalcocert.github.io/JAlcocerT/create-streamlit-chatgpt/#a-multichat-with-streamlit)       |
| `Youtube Groq Summaries`     ✓  | [Source Code](https://github.com/JAlcocerT/phidata)  🐍[Container](https://github.com/JAlcocerT/Streamlit-MultiChat/pkgs/container/streamlit-multichat)  | Summaries of YT Videos with Groq. [Blog](https://jalcocert.github.io/JAlcocerT/summarize-yt-videos/)      |
| `Chat with PDF`        ✓      | [Source Code](https://github.com/JAlcocerT/ask-multiple-pdfs) 🐍  [Container](https://github.com/JAlcocerT/ask-multiple-pdfs/pkgs/container/ask-multiple-pdfs) | Chat with PDFs (OpenAI). [Blog](https://jalcocert.github.io/JAlcocerT/how-to-chat-with-pdfs/) |

These are **LLM related AI projects** that you can play with.

```mermaid
mindmap
  root((AI with RPi))
    AI
    ::icon(fas fa-robot)
      APIs
        OpenAI
        Anthropic
        Groq
      Docker Compose Configuration
      Portainer UI
    Hardware
      Raspberry Pi 4
        ::icon(fab fa-raspberry-pi)
    DevTools
      Python
      ::icon(fab fa-python)
      Docker Containers
      ::icon(fab fa-docker)
      GithubActions
      ::icon(fas fa-code-branch)
```

> These projects can have working container images for x86/ARM64.
{: .prompt-info }

![Understanding LangChain with PDF Project](https://raw.githubusercontent.com/JAlcocerT/ask-multiple-pdfs/main/docs/PDF-LangChain.jpg)
_Credits to AlejandroAO for The Diagram and Initial Project which I forked_


> I made a **Youtube Video** on the [PDF AI Tool](https://www.youtube.com/watch?v=e9hJZrT7HLw)
{: .prompt-info }

The images are build with **Github Actions** with QEMU for **MultiArch (X86/ARM64)**.

You can see them as[Github Packages](https://github.com/JAlcocerT?tab=packages)

```sh
#https://github.com/JAlcocerT/phidata/tree/main/Z_DeployMe
docker pull ghcr.io/jalcocert/phidata:yt-groq #https://github.com/users/JAlcocerT/packages/container/package/phidata


#https://github.com/JAlcocerT/Streamlit-MultiChat/pkgs/container/streamlit-multichat
docker pull ghcr.io/jalcocert/streamlit-multichat:latest #https://github.com/JAlcocerT/Streamlit-MultiChat/tree/main/Z_DeployMe

#https://github.com/JAlcocerT/ask-multiple-pdfs/tree/main/Z_Deploy_me
sudo docker pull ghcr.io/jalcocert/ask-multiple-pdfs:v1.0 #https://github.com/JAlcocerT/ask-multiple-pdfs/pkgs/container/ask-multiple-pdfs
```

You can goahead and deploy with a [Docker-Compose/Portainer](#ai-stack).

Or if you are now with Docker/Containers, let me guide you through the build process:

1. Lets clone each repository
2. Use each `Dockerfile` to build the container images from source
3. Tweak the [AI Stack](#ai-stack) with the name of the local image

> You will need **Docker installed**. And [Portainer UI](https://fossengineer.com/selfhosting-portainer-docker/) will be beneficial.
{: .prompt-info }

```sh
git clone https://github.com/JAlcocerT/phidata
git clone https://github.com/JAlcocerT/Streamlit-MultiChat
git clone https://github.com/JAlcocerT/ask-multiple-pdfs

cd ./phidata && sudo docker build -t phidata_yt_groq . && cd ..

cd ./Streamlit-MultiChat && sudo docker build -t streamlit-multichat . && cd ..

cd ./ask-multiple-pdfs && sudo docker build -t ask-multiple-pdfs . && cd ..
```

If you want to **try just [one of them](#ai-projects-quick-cli-setup)**, you can use a quick **Docker CLI** like so, when the image is build:

```sh
docker run -d \
  --name phidata_yt_groq \
  -p 8509:8501 \
  -e GROQ_API_KEY=your_api_key_here \
  phidata_yt_groq \
  streamlit run cookbook/llms/groq/video_summary/app.py

#ifconfig #to get to know the device local IP
```

You will see the [Youtube Groq summarizer](https://jalcocert.github.io/JAlcocerT/summarize-yt-videos/) at: `http://devicelocalip:8509`


This is a realiable and **DIY way of trying cool projects** out there! 


## AI Stack

These **custom AI apps** can run on Raspberry Pi4 (ARM64).

If you have the **API Keys** and [Docker](#faq) installed...

* https://platform.openai.com/api-keys
* https://console.groq.com/keys
* https://console.anthropic.com/settings/keys

Just use [this **configuration**](https://github.com/JAlcocerT/Docker/blob/main/AI_Gen/Project_AIs/docker-compose.yml) to spin the 3 AI services:

```sh
curl -o docker-compose.yml https://raw.githubusercontent.com/JAlcocerT/Docker/main/AI_Gen/Project_AIs/docker-compose.yml

docker-compose up -d
```

You can use it as well via **Portainer UI as a Stack**:

```yml
services:
  # streamlit-chat-pdfs:
  #   image: ghcr.io/jalcocert/ask-multiple-pdfs:v1.0  #BUILD IT FOR ARM64 First
  #   container_name: chat_multiple_pdf
  #   volumes:
  #     - ai_chat_multiple_pdf:/app
  #   working_dir: /app  # Set the working directory to /app
  #   command: /bin/sh -c "export OPENAI_API_KEY='your_api_key_here' && streamlit run appv3_pass.py"    
  #   #command: tail -f /dev/null
  #   ports:
  #     - "8501:8501"    
  #   restart: unless-stopped

  streamlit-multichat:
    image: ghcr.io/jalcocert/streamlit-multichat #:v1.0
    container_name: streamlit_multichat
    volumes:
      - ai_streamlit_multichat:/app
    working_dir: /app
    command: /bin/sh -c "\
      mkdir -p /app/.streamlit && \
      echo 'OPENAI_API_KEY = \"sk-proj-openaiAPIhere\"' > /app/.streamlit/secrets.toml && \
      echo 'GROQ_API_KEY = \"gsk_groqAPIhere\"' >> /app/.streamlit/secrets.toml && \
      echo 'ANTHROPIC_API_KEY = \"sk-ant-yourANTHROPICapihere\"' >> /app/.streamlit/secrets.toml && \      
      streamlit run Z_multichat.py"
    ports:
      - "8501:8501"
    restart: always
    environment:
      MODEL_API_KEY: sk-proj-openaiAPIhere
      MODEL: gpt-4o-mini      #gpt-4 
      TEMPERATURE: 0 #dont be creative :)    
    #restart: always   

  phidata_yt_groq:
    image: ghcr.io/jalcocert/phidata:yt-groq #phidata_yt_groq
    container_name: phidata_yt_groq
    ports:
      - "8502:8501"    
    environment:
      - GROQ_API_KEY=your_api_key_here # your_api_key_here
    command: tail -f /dev/null #streamlit run cookbook/llms/groq/video_summary/app.py
    restart: unless-stopped

volumes:
  ai_streamlit_multichat:

volumes:
  ai_chat_multiple_pdf:
```

See how each AI Project is consuming resources:

```sh
htop
sudo docker stats streamlit_multichat
```

> With 4GB its more than enough! I got **~400mb/3.71GB of RAM**
{: .prompt-info }

---

## FAQ

Get **Docker** ready for [SelfHosting, like so](https://jalcocert.github.io/Linux/docs/linux__cloud/selfhosting/).

You can also try the projects separately with just Python and the required API's.

Make sure to setup a **proper [Python Venv](https://jalcocert.github.io/JAlcocerT/useful-python-stuff/)**.

More [**Vector DataBases** - Docker Config Files](https://github.com/JAlcocerT/Docker/tree/main/AI_Gen/Z_VectorDBs)

The **diagram** has been possible thanks to [MermaidJS](https://jalcocert.github.io/JAlcocerT/ai-useful-yet-simple/#diagrams-with-ai) Jekyll Integration and the [Fontawsome Icons](https://fontawesome.com/v5/search?o=r&m=free)

![Streamlit MultiChat Image](https://raw.githubusercontent.com/JAlcocerT/Streamlit-MultiChat/main/streamlit-multichat.png)


### AI Projects Quick CLI Setup

Some of these projects require APIs:

```sh
export OPENAI_API_KEY="sk-proj-openaiAPIhere"
export GROQ_API_KEY="gsk_groqAPIhere"
export ANTHROPIC_API_KEY="sk-ant-yourANTHROPICapihere"
export MODEL_API_KEY="sk-proj-openaiAPIhere"
```

1. You can [chat with PDFs thanks to this Streamlit App](https://jalcocert.github.io/JAlcocerT/how-to-chat-with-pdfs/):

```sh
sudo docker run -d \
  --name chat_multiple_pdf \
  -v ai_chat_multiple_pdf:/app \
  -w /app \
  -e OPENAI_API_KEY=your_api_key_here \
  -p 8501:8501 \
  ghcr.io/jalcocert/ask-multiple-pdfs:v1.0 \
  /bin/sh -c "streamlit run appv3_pass.py"
```

2. For the [Streamlit MultiChat Project](https://jalcocert.github.io/JAlcocerT/create-streamlit-chatgpt/):

```sh
sudo docker run -d \
  --name streamlit_multichat \
  -v ai_streamlit_multichat:/app \
  -w /app \
  -p 8501:8501 \
  -e MODEL="gpt-4o-mini" \
  -e TEMPERATURE="0" \
  ghcr.io/jalcocert/streamlit-multichat \
  /bin/sh -c "\
    mkdir -p /app/.streamlit && \
    echo 'OPENAI_API_KEY = \"$OPENAI_API_KEY\"' > /app/.streamlit/secrets.toml && \
    echo 'GROQ_API_KEY = \"$GROQ_API_KEY\"' >> /app/.streamlit/secrets.toml && \
    echo 'ANTHROPIC_API_KEY = \"$ANTHROPIC_API_KEY\"' >> /app/.streamlit/secrets.toml && \
    streamlit run Z_multichat.py"
```