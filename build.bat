:: Download dependencies and build docs

@echo off

echo BUILDING DOCS
py -3.11 -m pip install sphinx

echo UPDATING DEPENDENCIES
py -3.11 -m pip install -r docs/source/requirements.txt

echo BUILDING DOCS
py -3.11 -m sphinx.cmd.build -b html docs/source docs/build

echo OPENING DOCS IN BROWSER
start "" "docs/build/index.html"
