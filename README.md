# AQA Computer Science Password Manager NEA

This is a password manager made for my A-level Computer Science coursework, complete with GUI, encryption and a relational database.

## Prerequisites

Before running, you need to perform some steps:
* Install dependencies
* Create config files

### Installing dependencies

Running the `install-dependencies.bat` file should do this for you, but if this does not work, here are the packages you need to install with pip:
* PyQt5
* argon2-cffi
* cryptography

### Creating config files

Create a file in the main directory called `email.txt`, and it's contents should be:
```
example@examplemail.com:examplepassword
```
Note that this has only been tested with gmail accounts with insecure app access enabled, and likely will not work with other email services.

## Usage
Once the two prerequisite tasks have been completed, open `main.py` to use the application.
