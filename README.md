
# pharmex client front

##### Проброс порта
```bash
ssh -L 35672:localhost:15672 -L 3335:localhost:5672 -L 3334:localhost:6379 -L 3334:vita.citioj9smjkf.eu-west-1.rds.amazonaws.com:6379  -i gotaxiapp.pem ubuntu@ec2-34-245-223-245.eu-west-1.compute.amazonaws.com
```
##### Универсальный модуль с базовыми классами:
```bash
git submodule add git@bitbucket.org:mmdost/kinetic-core.git modules/kinetic_core
```

##### Обновление репозитариев
```bash
git pull --recurse-submodules 
```

##### Обновление репозитариев - если пред. не работает
```bash
git submodule update --init --force --remote
```

##### Установка зависимостей
```bash
pip install -r modules/kinetic_core/requirements.txt
```

##### установка другого конфига:
```python
import os
os.environ['VITA_CONFIG'] = '/var/www/config.py'
```
##### Пример регистрации executor:
Если лимит установлен в 1 - может существовать только 1 подписчик на 
события из RabbitMQ, если 0 - сколько угодно
```python

# Регистрируем наш слушатель - он принимает сообщения из очереди rabbitMQ
@executor(SomeExecutor, limit=1)
class TestQueueListener(QueueListener):

    async def parse(self, task):
        await SomeExecutor(task).parse()
        

main_loop = asyncio.get_event_loop()
main_loop.create_task(TestQueueListener().register_listener(main_loop))
main_loop.create_task(fill_some_products())
main_loop.run_forever()
```
##### Пример интерфейса:
```python
@executor(TestExecutor)
class TestClient(AbstractClient):

    @rpc
    async def add(self, data=None):
        pass
        
    @rpc(expiration=10)
    async def add_with_timeout(self, data=None):
        pass
        
    @lpc
    async def list(self):
        pass
        
    @event
    async def notify(self, message):
        pass
        
    @event(delay=1000)
    async def notify(self, message):
        pass
```
##### Пример обработчика:
```python
class TestExecutor(AbstractClient):

    async def add(self, data=None):
        # сохраняем в редис
        await self.save({"key": data})
        # do something on remote machine and return result
        pass
        
    async def list(self):
        # do something in same loop on client machine and return result
        pass
    
    async def notify(self, message=None):
        # this function does not return a response
        pass
```
