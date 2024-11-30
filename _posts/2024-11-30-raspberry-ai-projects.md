---
title: AI Projects on a Raspberry Pi
author: JAlcocerT
date: 2024-11-30
categories: [Make your Raspberry Useful]
tags: [AI]
mermaid: true
---

These year the Pi5 was launched.

What a perfect oportunity that was to get finally a Raspbery Pi 4 with a good price and do some AI projects with it.

This time I got a 4GB Pi4, ARM64!

Let's do some cool stuff with it.

- [ ] Raspberry Pi can do more than IoT. Go AI with a RPi
  + [x] [Python](#faq) Checks 👇
  + [ ] [Docker](#faq) Checks
  + [ ] Third Party APIs: OpenAI, Anthropic, Groq, also Ollama!
  + [ ] [Use AI Tools](#ai-stack) with your Raspberry Pi  

| Project             | Code                  | Use Case |
|---------------------|:---------------------:|:-----------:|
| `Streamlit Multi-Chat`  ✓  | [Source Code](https://github.com/JAlcocerT/Streamlit-MultiChat)  🐍 [Container](https://github.com/JAlcocerT/phidata/pkgs/container/phidata)      | Chat with Several LLMs via APIs. See [Blog](https://jalcocert.github.io/JAlcocerT/create-streamlit-chatgpt/#a-multichat-with-streamlit)       |
| `Youtube Groq Summaries`     ✓  | [Source Code](https://github.com/JAlcocerT/phidata)  🐍[Container](https://github.com/JAlcocerT/Streamlit-MultiChat/pkgs/container/streamlit-multichat)  | Quick Summaries of YT Videos with a Streamlit App. [Blog](https://jalcocert.github.io/JAlcocerT/summarize-yt-videos/)      |
| `Chat with PDF`        ✓      | [Source Code](https://github.com/JAlcocerT/ask-multiple-pdfs) 🐍  [Container](https://github.com/JAlcocerT/ask-multiple-pdfs/pkgs/container/ask-multiple-pdfs) | Chat with PDFs with OpenAI. [Blog](https://jalcocert.github.io/JAlcocerT/how-to-chat-with-pdfs/) |

These are **LLM related AI projects** that you can play with.

```mermaid
mindmap
  root((dht2influxdb))
    Software
      InfluxDB
      ::icon(fas fa-database)
      Python
      ::icon(fab fa-python)
        Adafruit_DHT Package
        InfluxDB Package
      Dockerfile
        Docker Compose Configuration
    Hardware
      Raspberry Pi 4
        DHT11 Temp Sensor
        ::icon(fas fa-thermometer-three-quarters)
        Three wires
    Tools
      Home Assistant
      Docker
```

> These projects have working container images for x86/ARM64. Feel free to run them not only with RPi's
{: .prompt-info }


<!-- ![BMAX B4 - Sysbench Test](/img/minipc-vs-pis/sysbench_bmaxb4.png)
_BMAX B4 - Sysbench Test_ -->

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

## AI Stack



```yml
version: '3'

services:
  streamlit-chat-pdfs:
    image: ghcr.io/jalcocert/ask-multiple-pdfs:v1.0 
    container_name: chat_multiple_pdf
    volumes:
      - ai_chat_multiple_pdf:/app
    working_dir: /app  # Set the working directory to /app
    command: /bin/sh -c "export OPENAI_API_KEY='your_api_key_here' && streamlit run appv3_pass.py"    
    #command: tail -f /dev/null
    ports:
      - "8501:8501"    
    restart: unless-stopped

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
    image: ghcr.io/jalcocert/phidata:yt-groq #phidata:yt_summary_groq
    container_name: phidata_yt_groq
    ports:
      - "8502:8501"    
    environment:
      - GROQ_API_KEY=your_api_key_here # your_api_key_here 🖕
    command: tail -f /dev/null #streamlit run cookbook/llms/groq/video_summary/app.py
    restart: unless-stopped

volumes:
  ai_streamlit_multichat:

volumes:
  ai_chat_multiple_pdf:
```

---

## FAQ

More [**Vector DataBases** - Docker Config Files](https://github.com/JAlcocerT/Docker/tree/main/AI_Gen/Z_VectorDBs)