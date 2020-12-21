# DOTA2BOT for QQ

# This branch has been deprecated, please switch to branch `new`

## Introduction

## Quick start

### Prepare

Install and run [OPQ](https://github.com/OPQBOT/OPQ)

Install [Docker](https://docs.docker.com/engine/install/)

### Run
Pull docker image from [DockerHub](https://hub.docker.com/r/zegwe/dota2bot)
```bash
docker pull zegwe/dota2bot:latest
```

Create `playerInfo.db` file.
```bash
mkdir Dota2Bot
cd Dota2Bot
touch playerInfo.db
```

Create and edit `config.json` file
```bash
vim config.json
```
Here's an example for `config.json`
```json
{
	"api_key": "xxxxx",
	"bot_qq": 1234567890,
	"admin_qq": 1234567890,
	"qq_group_id": 1234567890,
	"opq_url": "http://127.0.0.1:8080",
	"is_update_DOTA2": true,
	"player_list": [
		["圣果皇", 280353932, 1234567890]
	] 
}
```

Run with `Docker`.
```bash
docker run -itd -v $(pwd)/config.json:/opt/dota2bot/config.json -v $(pwd)/playerInfo.db:/opt/dota2bot/playerInfo.db --name dota2bot zegwe/dota2bot:latest
```
