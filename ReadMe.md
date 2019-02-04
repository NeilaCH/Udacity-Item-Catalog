# Item Catalog Application
Item Catalog application is a project for the Full Stuck Udacity [Nanodegree program](https://www.udacity.com/nanodegree).
The project consists of creating an application that provides a list of items within a variety of categories. User can registre to the application within an  authentication system. Only registered users can post, edit and delete their own items. 
# Project Structure
The Item Catalog Application is based on the following structure: 
-main.py
- list_itmcateg.py
- database_setup.py
- client_secrets.json
- static / style.css
- templates /
   - basic.html
   - main.html
   - in_category.html
   - delete_category.html
   - edit_category.html
   - login.html
   - new-category.html
   - new-item-2.html
   - new-item.html
   - update-item.html
   - delete_item.html
   - view-item.html

# Installing Requirements
Step 1. Before running The Item Catalog Application you must have the following elements on your machine:
* Python2.7, you can easily download it [here](https://www.python.org/downloads/).
* Virtual Box,  you can easily download it [here](https://www.virtualbox.org).
* Vagrant, you can easily download it [here] (https://www.vagrantup.com). After Installing vagrant, use your terminal and type `$ vagrant --version` to check if Vagrant is successfully installed.
* The latest version of Flask 1.x.

Step2. Download the Virtual Machine (VM) configuration [here](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip). After unziping the file, you will get the `fullstack-nanodegree-vm` repository containing the VM files.

Step3. To start your virtual machine (VM), inside your terminal:
* `cd` the `fullstack-nanodegree-vm` repository, then type `ls`.
* `cd`the vagrant/ subdirectory, then type `ls`.
* Run the command `vagrant up` to download and install the Linux operating system.
* Run `vagrant ssh` to log in the virtual machine (VM).

Now your machine is ready to run the Item Catalog Application.

# Instructions to Run the Project
Step1. Download the Item Catalog Application and unzip it.
Step2. Copy `Home_Catalog` folder into `fullstack-nanodegree-vm/vagrant`
Step3. download the data [here](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip) and unzip it. After that copy the `newsdata.sql` into `fullstack-nanodegree-vm/vagrant`
Step4. In your terminal, run `vagrant@vagrant:~$ cd /vagrant/Home_Catalog`
Step5. Run `database_setup.py`with this command 
`vagrant@vagrant:/vagrant$ python database_setup.py` in your terminal.
Step6. Run `list_itmcateg.py`with this command 
`vagrant@vagrant:/vagrant$ python list_itmcateg.py` in your terminal.
Step7. Once items and categories are succesfully added, run `main.py`with this command `vagrant@vagrant:/vagrant$ python main.py`.

As result, the terminal will display [a localhsot link](http://localhost:8000/). Use your favorite browser to open it.

### License
* The [Virtual Machine (VM) configuration](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip) used in this porject is provided by [Udacity](https://www.udacity.com).
