# DOTA2BOT for QQ

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
cd Dota2Bot
touch playerInfo.db
```

Create and edit `config.json` file
```bash
vim config.json
```

Run with `Docker`.
```bash
docker run -itd -v $(pwd)/config.json:/opt/dota2bot/config.json -v $(pwd)/playerInfo.db:/opt/dota2bot/playerInfo.db --name dota2bot zegwe/dota2bot:latest
```
