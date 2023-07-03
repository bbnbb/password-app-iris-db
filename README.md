# password-app-iris-db
Application for storing passwords, contains the functionality of registration / authorization.

After registration, you have access to the functionality of storing passwords protected by an encryption key, individual for each user.

This application uses nativeAPI to work with IRIS.

## How to use it 

To start the application, clone project:
 ```
$ git clone https://github.com/bbnbb/password-app-iris-db
```
And run the commands:
```
$ docker-compose up -d 
```
Then open [http://127.0.0.1:8011](http://localhost:8011/)

go to http://localhost:8011/register , and add a user
![image](https://github.com/bbnbb/password-app-iris-db/assets/15561051/6069219d-5650-4435-9b0b-61c476155592)

after that you will be redirected to the login page where you can log in
![image](https://github.com/bbnbb/password-app-iris-db/assets/15561051/ed750560-f7de-4666-8efb-b233cd83cd4c)

in case of incorrect data, you will be shown an authorization error

after successful login you will be redirected to http://localhost:8011/dashboard page where you can manage your passwords.
![image](https://github.com/bbnbb/password-app-iris-db/assets/15561051/33f85114-88df-4358-87d8-0f458164b24f)


The functionality of viewing previously saved passwords is available (by clicking on *********), as well as copying to the clipboard by clicking on the corresponding button. As well as the functionality of deleting previously saved passwords.

To add passwords, a form for adding a password is provided.
![image](https://github.com/bbnbb/password-app-iris-db/assets/15561051/f47ec811-4f8e-4d13-8d7b-10f8fe49b2b4)


## Technologies Used

- Python
- Iris-community
- Flask
- HTML/CSS
- JavaScript


