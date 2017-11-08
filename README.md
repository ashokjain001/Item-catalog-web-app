Item Catalog Web Application  
===============================
This web application is developed as a requirement for Udacity's Full Stack Web Development Nanodegree Program. 

## Description
The objective of the project is to create a web application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Technology
This is a RESTful web application using the Python framework FLASK along with implementing third-party OAuth2 Google and Facebook authentication. Application uses sqllite for database and utilizes SQLAlchemy ORM to perform CRUD (create, read, update and delete) operations.

## Skills learnt and applied in this project:
* RESTful API.
* Python Flask framework.
* HTML, CSS and Jinja2 templating.
* OAuth2.
* SQLAlchemy ORM CRUD operation. 

## Requirements

Virtual Machine and Vagrant are required to run the web application, download and Install [Vagrant](https://www.vagrantup.com/downloads.html), [VM](https://www.virtualbox.org/wiki/Downloads) and [vagrant file](https://github.com/udacity/fullstack-nanodegree-vm) which contains all the setup.

## Download and setup

1. Download and Install [Vagrant](https://www.vagrantup.com/downloads.html), [VM](https://www.virtualbox.org/wiki/Downloads).
2. After installation navigate to vagrant subdirectory by running command cd vagrant in your terminal and download required project files by cloning this git repository mentioned below and contents will be shared with your virtual machine.
```
git clone https://github.com/ashokjain001/catalog.git
```
3. From inside the catalog folder launch the Vagrant VM (by typing vagrant up from the terminal and log in using vagrant ssh).
4. Run this web application within the VM by typing python application.py.
5. Access and test your application by visiting http://localhost:5000 locally on your browser.
