if [[ "$*" == *"-v"* ]]
then
    ARGS="-v"
fi

python3 -m black $ARGS contacts
python3 -m isort $ARGS contacts
python3 -m pflake8 $ARGS contacts
python3 -m pytest $ARGS contacts
