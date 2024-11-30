<div align="center">
  <h1>Raspberry Pi and IoT</h1>
</div>

<div align="center">
  <h3>Get Started with Single Board Computers with these 101 Guides and Projects</h3>
</div>


<p align="center">
  <a href="https://github.com/JAlcocerT/RPi?tab=MIT-1-ov-file#readme" style="margin-right: 5px;">
    <img alt="Code License" src="https://img.shields.io/badge/License-MIT-blue.svg" />
  </a>
  <a href="https://github.com/JAlcocerT/RPi/actions/workflows/pages-deploy.yml" style="margin-right: 5px;">
    <img alt="Jekyll Theme Workflow" src="https://github.com/JAlcocerT/RPi/actions/workflows/pages-deploy.yml/badge.svg" />
  </a>
  <a href="https://github.com/JAlcocerT/RPi/actions/workflows/python-dht-build.yml" style="margin-right: 5px;">
    <img alt="DHT CI/CD Workflow" src="https://github.com/JAlcocerT/RPi/actions/workflows/python-dht-build.yml/badge.svg" />
  </a>
  <a href="https://GitHub.com/JAlcocerT/RPi/graphs/commit-activity" style="margin-right: 5px;">
    <img alt="Maintained" src="https://img.shields.io/badge/Maintained%3F-yes-green.svg" />
  </a>
</p>

<p align="center">
  <a href="https://youtube.com/@JAlcocerTech">
    <img alt="YouTube Channel" src="https://img.shields.io/badge/YouTube-Channel-red" />
  </a>
</p>


Start your journey with a **Raspberry Pi and explore its role in IoT**, embedded computing, and data analytics, all on one compact board. 

[**See the Raspberry Pi Projects** →][demo]

You can also [get started with **Linux**](https://jalcocert.github.io/Linux/) with a RPi. Also with [Docker](https://github.com/JAlcocerT/Docker).

The guides are available in Web version on: <https://jalcocert.github.io/RPi/>

> The web generated with the files of this repository and GH Actions.

## Guides Structure

* RPi Setup: first steps for new users and self-hosting
* IoT & Data Analytics: using sensors, Python, Docker and more.
* Networking: improving your home internet

In the folders starting with `Z_` you have supporting materials for the projects.

For example `Z_IoT` contains Scripts used in IoT Projects with the RPi.

## Powered Thanks To :heart:

* [Jekyll](https://github.com/jekyll/jekyll)
* [Jekyll Theme **Chirpy**](https://github.com/cotes2020/jekyll-theme-chirpy/)
* [Github Actions](https://fossengineer.com/docker-github-actions-cicd/)

* The fantastic community on the internet from where I learn the foundations to create all of this.

## :loudspeaker: Ways to Contribute 

Please feel free to fork the repository - **try it out the IoT Projects for yourself** and improve them!

<details>
  <summary>Local Web Dev with jekyll</summary>

```sh
#https://jekyllrb.com/docs/installation/
sudo apt install ruby-full build-essential zlib1g-dev && \
echo '# Install Ruby Gems to ~/.gem' >> ~/.bashrc && \
echo 'export GEM_HOME="$HOME/.gem"' >> ~/.bashrc && \
echo 'export PATH="$HOME/.gem/bin:$PATH"' >> ~/.bashrc && \
source ~/.bashrc && \
#gem update --system && \
gem install jekyll bundler

###https://www.ruby-lang.org/en/downloads/releases/
sudo apt install -y libssl-dev libreadline-dev zlib1g-dev libyaml-dev libffi-dev libgdbm-dev
curl -O https://cache.ruby-lang.org/pub/ruby/3.2/ruby-3.2.0.tar.gz
tar -xvzf ruby-3.2.0.tar.gz && cd ./ruby-3.2.0
./configure
make
sudo make install
ruby -v
```

</details>



Go to the theme folder and just do the following to see locally the website:

```sh
bundle
bundle exec jekyll s #local server - http://127.0.0.1:4000
#bundle exec jekyll serve --host 192.168.1.100 --port 4000
```

* Support the Projects that made possible this Project. I leveraged on their great job.

* Support extra evenings of tinkering and sharing Raspberry Pi / IoT stuff:

<p align="center">
  <a href="https://ko-fi.com/Z8Z1QPGUM">
    <img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="ko-fi" />
  </a>
</p>


[demo]: https://jalcocert.github.io/RPi/