# DOTA2BOT for QQ

## Introduction

This is [OPQ](https://github.com/OPQBOT/OPQ) based QQbot for watching group member's Dota2 game record.

This bot also integrates a plugin manager system, you can develop any plugin you want.

## Usage

> Notice: All the command are insensitive to half-width `!` and full-width `！`

### Plugin Manager

`!插件列表`: List all the plugins and their status(On or Off). Now it only support one plugin named [`Dota2Watcher`](), which is described below, but you can develop your own one.

`!启用插件 [index]`: Enable a plugin by its `index` in the list

`!禁用插件 [index]`: Disable a plugin by its `index` in the list

### Dota2Watcher

`!查看监视`: List all the players that is been watched.

`!添加监视 [nickname] [steam_id] [QQ account id]`: Add a player to be watched, by `nickname`, `steam_id` and `QQ account id`.

`!移除监视 [index]`: Remove a player from the watching list by its `index`

## Quick start

### Prepare

Install and run [OPQ](https://github.com/OPQBOT/OPQ)

Install [Docker](https://docs.docker.com/engine/install/)

### Run

You can [run python command directly](#run-python-directly) to debug, but **I strongly suggest you to use docker**, because it's better to run this bot in background.

You can [pull docker image from DockerHub](#use-dockerhub) or [build your own image from this repo](#use-git).

#### Use dockerhub

Pull docker image from [DockerHub](https://hub.docker.com/r/zegwe/dota2bot)
```bash
docker pull zegwe/dota2bot:latest
```

Create `pluginInfo.db` and `playerInfo.db` file.
```bash
mkdir Dota2Bot
cd Dota2Bot
touch playerInfo.db
touch pluginInfo.db
```


Create and edit `config.json` file
```bash
vim config.json
```
Here's an example for `config.json`, you can also see this as [`config.example.json`](./config.example.json) in repo
```json
{
	"api_key": "xxxxx",
	"bot_qq": 1234567890,
	"admin_qq": 1234567890,
	"groups": [1234567890], // this is a list of all the groups that you want to enable bot in
	"opq_url": "http://127.0.0.1:8080/v1/LuaApiCaller",
	"ws_url": "http://127.0.0.1:8080"
}
```

Run with `Docker`.
```bash
docker run -itd -v $(pwd)/config.json:/opt/dota2bot/config.json -v $(pwd)/playerInfo.db:/opt/dota2bot/playerInfo.db -v $(pwd)/pluginInfo.db:/opt/dota2bot/pluginInfo.db --name dota2bot zegwe/dota2bot:latest
```

#### Use git

Clone this repo
```bash
git clone https://github.com/ZegWe/Dota2Bot.git
```

Edit `config.json`
```bash
cd Dota2Bot
cp config.example.json config.json
vim config.json
```

Create `pluginInfo.db` and `playerInfo.db` file.
```bash
touch playerInfo.db
touch pluginInfo.db
```

Run with `docker-compose`
```bash
docker-compose up -d
```

#### Run python directly

Clone this repo
```bash
git clone https://github.com/ZegWe/Dota2Bot.git
```

Edit `config.json`
```bash
cd Dota2Bot
cp config.example.json config.json
vim config.json
```

Create `pluginInfo.db` and `playerInfo.db` file.
```bash
touch playerInfo.db
touch pluginInfo.db
```

Run with Python directly
```bash
pip install -r requirements.txt
python app.py
```
