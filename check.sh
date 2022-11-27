if [[ "$*" == *"-v"* ]]
then
    ARGS="-v"
fi

python3 -m black $ARGS src
python3 -m isort $ARGS src
python3 -m pflake8 $ARGS src
python3 -m pytest $ARGS src -v
