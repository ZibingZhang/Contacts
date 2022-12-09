if [[ "$*" == *"-v"* ]]
then
    ARGS="-v"
fi

python -m black $ARGS contacts
python -m isort $ARGS contacts
python -m pflake8 $ARGS contacts
#MYPYPATH="contacts" python -m mypy --explicit-package-bases $ARGS contacts
python -m pytest $ARGS contacts
