:: Download dependencies and build docs

py -3.11 -m pip install sphinx
py -3.11 -m pip install -r docs/source/requirements.txt
py -3.11 -m sphinx.cmd.build -b html docs/source docs/build
start "" "docs/build/index.html"
