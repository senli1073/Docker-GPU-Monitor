
![Github Forks](https://img.shields.io/github/forks/senli1073/Docker-GPU-Monitor?style=flat)
![Github Stars](https://img.shields.io/github/stars/senli1073/Docker-GPU-Monitor?style=flat)
![License](https://img.shields.io/github/license/senli1073/Docker-GPU-Monitor)
![Last Commit](https://img.shields.io/github/last-commit/senli1073/Docker-GPU-Monitor)

# Docker-GPU-Monitor

## Preview
![Screenshot of the Website](https://raw.githubusercontent.com/senli1073/Docker-GPU-Monitor/main/screenshot_full.png)

## Introduction

This project is a lightweight GPU monitor designed for real-time web-based viewing of GPU server status. It provides detailed information on GPU status and processes utilizing the GPU. The container names are displayed for processes running inside Docker containers, facilitating GPU monitoring for servers shared by multiple users.

## Getting Start
### 1. Clone this repository
Go to the folder where you want to store your project, and clone the new repository:
```
git clone git@github.com:senli1073/Docker-GPU-Monitor.git
```
### 2. Python environment preparation

`Python >= 3.7` is required.

Then install `numpy` and `Flask`:
```
pip install -r requirements.txt
```

### 3. Edit configuration

Edit the copyright information, page update interval, and port the website in `config.py`。

### 4. Deployment
You can choose method (a) or (b) to run this project:

(a) Run in `dev-mode`:
```
bash ./start_dev_app.sh
```
(b) Run in `production-mode`:
```
gunicorn --daemon -w 4 --access-logfile=./access.log  -b 127.0.0.1:80 app:app
```
### 5. Enjoy
Fire up a browser and go to `http://<server_ip_address>/`


## License
Copyright Sen Li, 2024. Licensed under an MIT license. 
