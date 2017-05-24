# Entrance-UM
Usermanagement (UM)

This python program is the frontend for Entrance users. It enables the user to maintain data (*.fit files, graphic files such as *.png or *.jpg) and to encrypt data under some access rules. The encryption backend is a Java service and needs to be setup seperatly. 

In order to use the Dashboard, please add a valid email provider information to https://github.com/SNET-Entrance/Entrance-UM/blob/master/src/config/default.py . This email provider will be used to send invitation emails to users trying to register to the Dashboard.


Preliminaries:

- rename src/config/default.py.example to src/config/default.py 
- edit src/config/default.py for your needs (provide valid email provider settings).

Initialize the Dashboard:
 	
	...$ cd src/
	.../src$ sudo python setup-database.py install 
	.../src$ sudo python setup.py install
	
Start the service:
	
	.../src$ python run.py
	
Check whether a hidden ".entrance" directory in your home folder exists.

# Login to the Dashboard using a test account: 
Testuser:Test1234

# Using an edugain account for login:
 After
 
 1st. defining a login/password for a SMTP server in config/default.py
 
 2nd. creating a local account using your edugain-ready email address,
 
 you can log into the Dashboard using your edugain credentials. Trigger the edugain login by clicking on the Cyclone logo at the login page.

# Dashboard Screenshot:
![alt text](https://github.com/SNET-Entrance/Entrance-UM/blob/master/Screenshot_Dashboard.jpg)
