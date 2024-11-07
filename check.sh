if [[ "$*" == *"-v"* ]]
then
    ARGS="-v"
fi

echo "black"
python -m black $ARGS contacts
echo "isort"
python -m isort $ARGS contacts
echo "pflake8"
python -m pflake8 $ARGS contacts
echo "mypy"
python -m mypy $ARGS contacts
echo "pytest"
python -m pytest $ARGS contacts
