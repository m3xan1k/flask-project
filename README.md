# flask-project
## По мотивам одного тестового задания

Исходное ТЗ: https://github.com/avezhenya/flask-project


1. Для хранения настроек в окружении:
    ./vars.sh 'your_secret_key' 'mysql://USER:PASS@HOST/digital_library'

    Для перманентного сохранения нужно добавить в конец ~/.profile записи

    SECRET_KEY='your_secret_key'
    SQLALCHEMY_DATABASE_URI='mysql://USER:PASS@HOST/digital_library'

2. Установка зависимостей:
    pip3 install -r requirements.txt

2. Для создания базы и схемы:
    mysql -u USERNAME -p -e 'source create.sql' && python3 create_schema.py

3. Запуск приложения:
    flask run