# THIS PROJECT IS NO LONGER MAINTAINED
# DOTA2BOT for QQ

- [DOTA2BOT for QQ](#dota2bot-for-qq)
	- [Introduction](#introduction)
	- [Usage](#usage)
		- [Plugin Manage](#plugin-manage)
		- [Dota2Watcher](#dota2watcher)
		- [Dota2Fortune](#dota2fortune)
		- [Dota2MDI](#dota2mdi)
	- [Quick start](#quick-start)
		- [Prepare](#prepare)
		- [Run](#run)
			- [Use dockerhub](#use-dockerhub)
			- [Use git](#use-git)
			- [Run python directly](#run-python-directly)
	- [Develop your plugin](#develop-your-plugin)

## [Introduction](#introduction)

This is [OPQ](https://github.com/OPQBOT/OPQ) based QQbot for watching group member's Dota2 game record.

This project is developed under Python3.9.

This bot also integrates a plugin manage system, you can develop any plugin you want.

## [Usage](#usage)

> Notice: All the command are insensitive to half-width `!` and full-width `！`.

|已支持插件|插件说明|
|-|-|
|[Dota2Watcher](#dota2watcher)|Dota2战绩监视|
|[Dota2Fortune](#dota2fortune)|Dota2每日运势|
|[Dota2MDI](#dota2mdi)|Dota2战绩图|

### [Plugin Manage](#plugin-manage)

`!插件列表`: List all the plugins and their status(On or Off).

`!启用插件 [index]`: Enable a plugin by its `index` in the list.

`!禁用插件 [index]`: Disable a plugin by its `index` in the list.

`!帮助`: Display help content.

`!插件帮助 [plugin_name]`: Display help content for a given plugin.

### [Dota2Watcher](#dota2watcher)

`!查看监视`: List all the players that is been watched.

`!添加监视 [nickname] [steam_id] [QQ account id]`: Add a player to be watched, by `nickname`, `steam_id` and `QQ account id`.

`!移除监视 [index]`: Remove a player from the watching list by its `index`.

### [Dota2Fortune](#dota2fortune)

`!今日运势`: Today's fortune of Dota2.

`!幸运英雄`: Today's lucky hero.

### [Dota2MDI](#dota2mdi)

`!战绩图 [match_id]`: return match detail image

## [Quick start](#quick-start)

### [Prepare](#prepare)

Install and run [OPQ](https://github.com/OPQBOT/OPQ)

Install [Docker](https://docs.docker.com/engine/install/) or Python, see the details below.

### [Run](#run)

You can [run python command directly](#run-python-directly) for debug, but **I strongly suggest you to use docker**, because it's better to run this bot in background.

Using docker, you can [pull docker image from DockerHub](#use-dockerhub) or [build your own image from this repo](#use-git).

#### [Use dockerhub](#use-dockerhub)

Pull docker image from [DockerHub](https://hub.docker.com/r/zegwe/dota2bot)
```bash
docker pull zegwe/dota2bot:latest
```

Create `botInfo.db` file.

```bash
mkdir Dota2Bot
cd Dota2Bot
touch botInfo.db
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
	"groups": [1234567890],
	"opq_url": "http://127.0.0.1:8080",
	"debug": false,
	"mdi_url": "http://dota2mdi.zegwe.me"
}
```

Run with `Docker`.

```bash
docker run -itd -v $(pwd)/config.json:/opt/bot/config.json -v $(pwd)/botInfo.db:/opt/bot/botInfo.db --name dota2bot zegwe/dota2bot:latest
```

#### [Use git](#use-git)

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

Create `botInfo.db` file.

```bash
touch botInfo.db
```

Run with `docker-compose`

```bash
docker-compose up -d
```

#### [Run python directly](#run-python-directly)

Install [`Python3.9`](https://www.python.org/downloads/)

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

Run with Python directly

```bash
pip install -r requirements.txt
python app.py
```

## [Develop your plugin](#develop-your-plugin)

To develop your own plugin, you should follow these rules:

1. Your plugin should be a subclass of [`Plugin`](/model/plugin.py) in the model folder.
2. Add your command in the `__init__` method. You can reference other plugins in [plugins](/plugins) folder.
3. Put your plugin file/folder into the [plugins](/plugins) folder, and import it in the [\_\_init__.py](/plugins/__init__.py) file.
4. Add your plugin in [app.py](/app.py) by `add_plugin` method.
