run:
    python3 src/main.py

lint:
    pip install autopep8 pylint
    autopep8 -aaa --in-place src/*.py
    pylint src/*.py

install-deps:
    pip install -r src/requirements.txt

clean:
    pip freeze | xargs pip uninstall -y
    rm -rf dist/ build/ main.spec src/__pycache__/

build:
    pip install pyinstaller
    pip install -r src/requirements.txt
    cd src && pyinstaller \
        --onefile \
        --noconsole \
        --icon=favicon.ico \
        --distpath ../dist \
        main.py
