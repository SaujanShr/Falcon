# Team Falcon Small Group project

## Team members
The members of the team are:
- Saujan Shrestha
- Patryk Kugla
- Quan Tran
- Yu Han Chen
- Anton Sirgue

## Project structure
The project is called `msms` (Music School Management System).  It currently consists of a single app `lessons` where all functionality resides.

## Deployed version of the application
The deployed version of the application can be found at *<[Falcon Music School](https://yc7.pythonanywhere.com)>*.

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

Make the database migrations:
```
$ python3 manage.py makemigrations
```

Migrate the database:

```
$ python3 manage.py migrate
```

Create authentication groups:

```
$ python3 manage.py create_groups
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

The image used in the Home view is free of rights.
It was sourced from: https://pixabay.com/photos/piano-sheet-music-music-keyboard-1655558/?download
And is specified to be placed "Free to use under the Pixabay license." with "No attribution required"
*Declare are other sources here.*
