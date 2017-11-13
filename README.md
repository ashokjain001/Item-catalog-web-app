Item Catalog Web Application  
===============================
Live web app can be found at [Catalog APP](https://catalogappy.herokuapp.com/).
This web application is developed as a requirement for Udacity's Full Stack Web Development Nanodegree Program. 

## General Description
The objective of the project is to create a web application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Technical Description
This is a RESTful web application using the Python framework FLASK along with implementing third-party OAuth2 Google and Facebook authentication. Application uses sqllite for database and utilizes SQLAlchemy ORM to perform CRUD(create, read, update and delete) operations.

## Skills learnt and applied in this project:
* RESTful API.
* Python Flask framework.
* HTML, CSS and Jinja2 templating.
* OAuth2 3rd party user authentication using Google and Facebook.
* SQLAlchemy ORM CRUD operation. 
* Heroku app deployment

## Requirements

Virtual Machine and Vagrant are required to run the web application.

## Download and setup

1. Download and Install [Vagrant](https://www.vagrantup.com/downloads.html), [VM](https://www.virtualbox.org/wiki/Downloads).
2. After installation navigate to vagrant subdirectory by running command **cd vagrant** in your terminal and download required project files by cloning this git repository mentioned below and contents will be shared with your virtual machine.
```
git clone https://github.com/ashokjain001/catalog.git
```
3. From inside the catalog folder launch the Vagrant VM (by typing **vagrant up** from the terminal and log in using **vagrant ssh**).
4. Once Vagrant VM is up and running, run this web application in terminal by typing **python application.py**.
5. Access the application by visiting http://localhost:5000 locally on your browser. 

## Endpoints
 
**endpoints to access resources -** 

/catalog - displays all the catalogs and latest items. 

/catalog/<string:catalog>/items - displays all the items under catalog.

/login - login page.

/catalog/item/new - add a new item(login required).

/catalog/<string:item>/edit - display form to edit items(login required).

/catalog/<string:item>/delete - delete item(login required).


**JSON endpoints for API consumption -**

/catalog/JSON - show all catalogs.

/items/JSON - show all items.

/catalog/<string:catalog>/items/<string:item>/JSON - show specific item under a catalog.

/catalog/<string:catalog>/items/JSON - show all the items under a particular catalog.