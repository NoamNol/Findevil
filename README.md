# Findevil
Find evil content in YouTube comments

## Get started
```powershell
# in Linux replace 'set' with 'export'
set YOUTUBE_API_KEY=<your_key>
docker-compose up -d --build
```

Before `docker-compose up`, you can set more optional settings:
```powershell
# in Linux replace 'set' with 'export'
set ASYNC_WORKERS=<number>
set MONGODB_FLASK_USERNAME=<name>
set MONGODB_FLASK_PASSWORD=<password>
set MONGODB_ADMIN_USERNAME=<name>
set MONGODB_ADMIN_PASSWORD=<password>
```

### Send a request
> You can use tools like [Postman](https://www.postman.com/) to send HTTP requests.

Scan all comments of a YouTube video:
</br>
`http://127.0.0.1:5001/youtube/videos/<video_id>/comments` `[PUT]`

Or with `max` parameter:
</br>
`http://127.0.0.1:5001/youtube/videos/<video_id>/comments?max=<max>` `[PUT]`

### Connect to MongoDB
Now you can connect to the database and view the new data in `flaskdb` db.
</br>
The connection string is:
`mongodb://mongodbadmin:temp_admin_password@localhost:27019`

> Change `mongodbadmin` and `temp_admin_password`
if you used custom `MONGODB_ADMIN_USERNAME` and `MONGODB_ADMIN_PASSWORD`.

### Clean the database
To delete the users and data in MongoDB, run:
```
docker-compose down
docker volume rm findevil_mongodbdata
```

Now you can start again with fresh db and run `docker-compose up` as described above.

## Development
### Requirements
- Python 3.9
- Docker
### Build and run MongoDB for development
```powershell
cd mongo
docker build -t mongo-findevil:latest .
docker run --name mongodb-dev -p 27018:27017 --env-file .env.dev -d mongo-findevil:latest
```

Use port `27018` to connect to the `dev` database:
</br>
`mongodb://mongodbadmin:temp_admin_password@localhost:27018`

### Build and run Flask

Windows:
```powershell
cd flask
copy .env.dev .env
# edit your .env file...
py -m venv env
.\env\Scripts\activate
pip install -r requirements-dev.txt
flask run
```

Linux:
```shell
cd flask
cp .env.dev .env
# edit your .env file...
python3 -m venv env
source env/bin/activate
pip install -r requirements-dev.txt
flask run
```

Use port `5000` to send requests to the `dev` server:
</br>
`http://127.0.0.1:5000/youtube/videos/<video_id>/comments` `[PUT]`

### Debugging
To debug Flask, instead of `flask run` use the debugger in VSCode.