## Перед запуском нужно создать конфигурационный файл со следующим содержанием.

Название файла `.env`:

```
BOT_TOKEN='токен от бота'
GROUP_ID=идентификатор от публичной или частной группы
```

## Запуск бота.

### Docker
`docker-compose up --build`

### PM2
#### Создание вирутальной среды
```shell
python -m venv env
```

#### Активация вирутальной среды
```shell
source env/bin/activate
```

#### Установка зависимостей
```shell
pip install -r requirements.txt
```

#### Запуск
```shell
pm2 start main.py --name=cexbot
```