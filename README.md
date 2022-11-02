# Team *<enter team name here>* Small Group project

## Team members
The members of the team are:
- *<name of team member 1>*
- *<name of team member 2>*
- *<name of team member 3>*
- *<name of team member 4>*
- *<name of team member 5>*

## Project structure
The project is called `msms` (Music School Management System).  It currently consists of a single app `lessons` where all functionality resides.

## Deployed version of the application
The deployed version of the application can be found at *<[enter URL here](URL)>*.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Sources
The packages used by this application are specified in `requirements.txt`

*Declare are other sources here.*
