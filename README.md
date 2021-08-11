# Findevil
Find evil content in YouTube comments

## Development
### Requirements
- Python 3.9
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