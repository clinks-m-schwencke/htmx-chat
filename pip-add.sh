set -e

echo "Pip: Installing '$@'"
pip install "$@"

pip freeze > requirements.txt
