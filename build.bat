:: Download dependencies and buld docs

@echo off

echo:
echo BUILDING DOCS
echo:

py -3.11 -m pip install sphinx

echo:
echo UPDATING DEPENDENCIES
echo:

py -3.11 -m pip install -r docs/source/requirements.txt

echo:
echo BUILDING DOCS
echo:

py -3.11 -m sphinx.cmd.build -b html docs/source docs/build

echo:
echo OPENING DOCS IN BROWSER
echo:

start "" "docs/build/index.html"
