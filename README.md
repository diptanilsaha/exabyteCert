# exabyteCert

**exabyteCert** is a Flask Application, which can be used to generate Certificates and also serves the purpose of distribution of Certificates.

## Application Structure

```bash
exabyteCert
├── README.md
├── app
│   ├── __init__.py
│   ├── main
│   │   ├── __init__.py
│   │   ├── certs
│   │   │   └── certificates.pdf
│   │   ├── cli.py
│   │   ├── forms.py
│   │   ├── routes.py
│   │   └── templates
│   │       ├── certificates.html
│   │       └── index.html
│   ├── models.py
│   └── utils
│       ├── __init__.py
│       └── cert.py
├── config.py
├── example.env
└── requirements.txt
```

* **app/**: Application directory.
    * **main/**: Web application and CLI application is present in this directory.
        * **certs/**: Generated Certificates are stored here.
    * **utils/**: Utility tools are kept under this directory.
* **config.py**: Contains configuration of the Flask Appication.
* **requirements.txt**: Required Python Packages to run this Application.

## Installation

After cloning this repository, create a new `.env` file and copy the content of `example.env` to `.env` file and replace `YOUR_SECRET_KEY` with yours.

Assuming, you are a regular user of `virtualenv`, create and activate the Virtual Environment and run:

```bash
$ pip install -r requirements.txt
```

After installing the required packages, it must be told where your `FLASK_APP` is located. To do the same, run:

```bash
$ export FLASK_APP=app
```

`exabyteCert` uses Flask-Migrate in order to implement the Database Migration.

Run the following commands:

```bash
$ flask db init
$ flask db migrate -m "initial migration"
$ flask db upgrade
```

This will create the Database and apply migration.

## Command Line Application

The Command Line Application is made to generate Certificates and manage them.

In order to generate Certificates, follow the steps.

### Step 1: Event

#### Create Events

To create a event run:

```bash
$ flask certs create-events -e EventName
```

To create multiple events, run:

```bash
$ flask certs create-events -e Event1 -e Event2
```

#### Show all Events

To view all the events that were already created, run:

```bash
$ flask certs show-events
```

#### Update Event Name

To update name of an existing event, run:

```bash
$ flask certs update-event -o EventOldName -n EventNewName
```

**Note:** This command will not make changes on the Certificates.

#### Delete Event

To delete an existing event, run:

```bash
$ flask certs delete-event -e EventName
```

**WARNING:** This command will also delete all the Certificates linked with the Event.

### Step 2: Generate Certificates

To generate Certificates for a Event, run:

```bash
$ flask certs generate-certs -y [YAMLFILE] -c [CSVFILE] -e [EVENTNAME]
```

* **YAMLFILE:** Path of a YAML File containing all the Certificate Template, Font and other necessary instructions. The YAML File must follow the following format.

```YAML
template: "Blank-Certificate.jpg" # Blank Certificate
font:
  name: "FontName.ttf" # Truetype Font File
  size: 60 # Font Size
participantBox: [1687, 1263, 3073, 1351]
# Participant Name Box [Left, Top, Right, Bottom] in List
eventBox: [1280, 1387, 2172, 1475]
# Event Name Box [Left, Top, Right, Bottom] in List
title: "Certificate PDF Title" # PDF Title
author: "Author's Name" # Author's Name
```

* **CSVFILE:** Path of a CSV File containing the List of Participants of a Particular Event.

    *Tips: Try naming the csv file after an event.*

    The CSV File must follow the following format:
```csv
name,email
Name1,name1@email.com
...
```

* **EVENTNAME:** An Existing Event.

## Web Application

After Certificate generation, run the application:

```bash
$ flask run
```

The Application will run on 5000 port by default.

To run on your preferred port, replace `PORT_NUMBER` with your preferred port number and run:

```bash
$ flask run --port=<PORT_NUMBER>
```
