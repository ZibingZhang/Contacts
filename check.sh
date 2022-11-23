python3 -m black src
python3 -m isort -v src
python3 -m pflake8 src
python3 -m pytest src -vv
