# DOTA2BOT for QQ

## Introduction

## Quick start

### Prepare

Download [MiraiOK](https://github.com/LXY1226/MiraiOK).

Run `MiraiOK` once and close, there would be a `plugins` flolder.

move the jar file in [mirai-http-api](https://github.com/project-mirai/mirai-api-http) release int the plugins folder.

Run `MiraiOK` with `screen` and sgin in with your QQ account
```bash
screen -S bot && ./miraiOK_linux-amd64
```

### Install

Install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/)

Download this Repo
```bash
git clone https://github.com/ZegWe/Dota2Bot.git
```

Edit configuration file
```bash
cd Dota2Bot
cp config.example.json config.json
vim config.json
```

Run with docker-compose
```bash
docker-compose up -d
```
