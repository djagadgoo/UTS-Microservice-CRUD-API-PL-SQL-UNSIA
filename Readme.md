
# microservice CRUD AES256

aplikasi dengan bisa menggunakan CRUD dengan beberapa variabel sepserti email, password, fullname, dan juga job dan tidak lupa dengan eknripsinya

langkah  menjalankanya

1. clone project dan buka porjectnya
2. Buat Database dengan nama db_users
3. Sesuaikan konfigurasi database anda di app.py

      app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/db_users'


4. Install program Python 3

   [Download python](https://www.python.org/downloads/0)


5. langkah selanjutnya mengInstall Virtual Environment

    Set-ExecutionPolicy Unrestricted -Scope Process
    pip3 install virtualenv


6. lalu buat Virtual Environmentnya

    python -m venv venv


7. dan aktifkan Virtual Environment

    venv\Scripts\activate


    Nonaktifkan

    deactivate

8. Install requirement dengan menggunakan command

    pip install -r requirements.txt

    
9. selanjutnya buat migrations Database

    flask db stamp head
    flask db migrate -m 'your descriptive message'
    flask db upgrade
    
10. terakhir jalankan server

    flask run

langkah langkah ini di lakukan pada terminal