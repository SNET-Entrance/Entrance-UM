# Entrance-UM
Usermanagement (UM)

This python program it a frontend for Entrance users. It enables the user to maintain data (*.fit files, graphic files such as *.png or *.jpg) and to encrypt data under some access rules. The encryption backend is a Java service and need to setup seperatly. 

In order to use teh Dashboard, please add a valid email provider information to https://github.com/SNET-Entrance/Entrance-UM/blob/master/src/config/default.py . This email provider will be used to send invitation emails to users trying to register to the Dashboard.

Initialize the Dashboard:

...$ cd src/
.../src$ sudo python setup-database.py install 
.../src$ sudo python setup.py install

Run the Service:

.../src$ python run.py

Check whether a hidden ".entrance" directory in your home folder exists.

