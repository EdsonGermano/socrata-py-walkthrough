# `socrata-py` walkthrough
This is a little repo to help get you using socrata-py. It's really just a collection of examples.

## Setup
run `./setup`

Edit `examples/auth.py` and fill in your target domain, username, and password.

## Adventure
After running `./setup`, there is a choose your own adventure game which walks through some
of the concepts relevant to the ETL process

## Examples
After running `./setup`, run `source venv/bin/activate` to activate the virtual env.
Then run

```
python -m examples.create_dataset
```
or
```
python -m examples.create_shapefile
```
etc. Look in the `examples` dir for examples.

These examples are semi-interactive; they will launch browser windows to take you to
the relevant UI component. If you wanted to adapt them to a scripting environment, you would remove the `open_in_browser` and `input` calls.
