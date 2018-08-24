# TODO

- [ ] Environment variables
- [ ] Example `.env`
- [ ] Accept MFA for local execution 
- [ ] Consistent with [GDS Way](https://gds-way.cloudapps.digital/manuals/programming-languages/python/python.html#writing-python-at-gds)
- [ ] Unit tests
- [ ] Dockerfile


### Developer Setup 

#### Install prerequisites

- Python 3
  ```
  brew install python3
  ```
- Precommit - for installing hooks that run final checks before allowing push to repositories
  ```
  brew install pre-commit
  ```
  
#### Set up dependencies
```
make requirements-dev
```

#### Intellij Setup

After creating the virtual environment (as outlined above):
- On the IntelliJ start page, select `Import Project`
- Choose the root folder of this project (`verify-performance-scripts`), then `Next`
- Select the option `Import project from existing sources`
- Continue until the `Select SDK` screen, where we will configure Intellij to use the Virtualenv
  - Click `+` on the top-left to add sdk 
  - choose `Virtualenv environment`, `Existing environment` 
  - set the `Python Interpreter` field to the file `verify-performance-scripts/venv/bin/python3`
- Continue until end of setup.


### Working with the codebase

#### Using the Virtualenv
We are using an isolated Python environment, venv, to allow modules, etc used by one project to not affect another
From the project root directory, run the following in terminal:
```
make virtualenv
```

While working, run the following command to switch into the virtual environment
```
source ./venv/bin/activate
```

To exit the virtual environment:
```
deactivate
```