# Проектная работа 9 спринта

Задания на спринт вы найдёте внутри тем.

## Структура данных
###  Film TimeStamp
#### API
- jwt: JWT
- film_id: uuid.UUID
- film_timestamp: datetime.datetime
- event_time: datetime.datetime 
#### ETL
- user_id: str
- film_id: uuid.UUID
- film_timestamp: datetime.datetime
- event_time: datetime.datetime 
### Like
#### API
- jwt: JWT
- film_id: uuid.UUID
- score: int
- event_time: datetime.datetime 
#### ETL
- user_id: str
- film_id: uuid.UUID
- score: int
- event_time: datetime.datetime 
### BookMark
#### API
- jwt: JWT
- film_id: uuid.UUID
- event_time: datetime.datetime 
#### ETL
- user_id: uuid.UUID
- film_id: uuid.UUID
- event_time: datetime.datetime 
### Review
#### API
- jwt: JWT
- film_id: uuid.UUID
- meta:
  - author: uuid.UUID
  - likes: List[uuid.UUID]
  - dislikes: List[uuid.UUID]
  - review_time: datetime.datetime 
- event_time: datetime.datetime 
#### ETL
- user_id: uuid.UUID
- film_id: uuid.UUID
- meta:
  - author: uuid.UUID
  - likes: List[uuid.UUID]
  - dislikes: List[uuid.UUID]
  - review_time: datetime.datetime 
- event_time: datetime.datetime 

### Ссылка
  https://github.com/Chelovek760/ugc_sprint_2_g
### Запуск
- C dev окружением:  
docker-compose -f docker-compose-dev.yml up
- С prod окружением:  
docker-compose up    
- Сервис будет доступен по http://localhost:8000
- Документация 
http://localhost:8000/api/docs
  <br/>
  <br/>
### Задачи
См. [issue](https://github.com/Chelovek760/ugc_sprint_2_g/issues)
### Результаты анализа
См. [benchmark](https://github.com/vlad397/ugc_sprint_2/tree/main/benchmark/mongo)

### Принципиальная схема работы
1. Post предобрабатываются и отпраляются из [ugc_api](https://github.com/vlad397/ugc_sprint_2/tree/main/ugc_api) kafka 
2. [etl](https://github.com/vlad397/ugc_sprint_2/tree/main/etl) реализуется Kafka->Mongo
3.  Get ugc_api -> mongo -> client

