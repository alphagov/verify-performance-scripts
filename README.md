# TODO

- [x] Environment variables
- [ ] Example `.env`
- [x] Accept MFA for local execution 
- [ ] Consistent with [GDS Way](https://gds-way.cloudapps.digital/manuals/programming-languages/python/python.html#writing-python-at-gds)
- [ ] Unit tests
- [ ] Dockerfile

### Developer Setup 

#### Install prerequisites

- Python 3
  ```bash
  brew install python3
  ```
- Pre-commit - for installing hooks that run final checks before allowing push to repositories
  ```bash
  brew install pre-commit
  ```
  
#### Set up dependencies
```bash
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

#### Running tests
Tests can be run by executing `make test`.

#### Git hooks
We are using `pre-commit` to setup Git hooks automatically based on configurations defined within 
`.pre-commit-config.yaml`. 

In order to setup the hooks, you should execute the `./pre-commit` script provided with this 
repository. It will ask you to install `pre-commit` if it isn't already installed. It will use 
`pre-commit` to automatically install pre-push Git hooks in order to only allow push if tests 
pass.

#### Installing dependencies
Application and development dependencies are specified in `requirements-app.txt` and 
`requirements-dev.txt` respectively.

If you need to install dependencies for local development, execute `make requirements-dev`. This 
will install application as well as development dependencies. 

You can freeze your versions of 
application dependencies by running `make freeze-requirements`, which will generate 
`requirements.txt` containing the specific versions of application dependencies installed on your 
environment. Building reproducible environments then becomes easier by executing 
`make requirements`, which will only install dependencies specified in `requirements.txt`.
