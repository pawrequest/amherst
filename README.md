# amherst

This project pulls together a number of different tools to assist with our day-to-day business needs.

It is ludicrously over-engineered. Previous iterations used PySimpleGui, but that is no longer FOSS - instead we produce a full FastAPI based web-application wrapped in FlaskWebGui to render as a desktop app.


## Major Dependencies

- ### Commence RM Designer Edition
    CRM
- ### Pydantic
    type safety, validation, serialisation
- ### FastAPI
    manage endpoints and application flow / concurrency
- ### Htmx
    front-end tooling
- 
~~### SqlModel~~ 
~~- use Sqlite DB as persistent storage~~  
~~### FastUi~~
~~- declarative front-end from the Pydantic Family~~

### Logguru
- could be removed but frankly i like it

## Custom (pawrequest) Dependencies

### [PyCommence](https://github.com/pawrequest/pycommence) 
- a nascent ORM (currently just simple CRUD) to access Commence RM Designer edition via python
- next version is creating json-schema from the db data and dynamically defininf Pydantic Models / SQL schema 

### [Shipaw](https://github.com/pawrequest/shipaw) 
- a shipping client to book collections and produce labels
- currently uses Parcelforce's ExpressLink API but could easily be replaced with other suppliers

### [PawDantic](https://github.com/pawrequest/pawdantic)
- tools for working in the Pydantic ecosystem, specifically custom types like `TruncatedPrintableString(length:int)`, `ValidUkPostcode`

### [PawRequest/FlaskWebGui](https://github.com/pawrequest/FlaskWebGui) 
- a fork of Climente's FlaskWebGui injecting a 'URL_Suffix' param to allow dynamic definiition of the initially loaded URL

### [PawDF](https://github.com/pawrequest/pawdf)
-PDF tooling, specifically for arraying the A6 labels Parcelforce provide on A4 - 2 to a page - and sending to printer

### [Suppawt](https://github.com/pawrequest/suppawt)
- general pytyon support

## Dev Dependencies
### pytest
### sphinx + autodoc + napoleon

