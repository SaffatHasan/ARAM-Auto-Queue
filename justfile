run:
    cd src && python3 main.py

lint:
    pip install autopep8 pylint
    autopep8 -aaa --in-place src/*.py
    pylint src/*.py

install-deps:
    pip install -r src/requirements.txt

clean:
    pip freeze | xargs pip uninstall -y
    rm -rf dist/ build/ main.spec src/__pycache__/

package: install-deps
    pip install pyinstaller
    cd src && pyinstaller \
        --onefile \
        --noconsole \
        --name "AutoQr" \
        --add-data "favicon.ico;." \
        --icon=favicon.ico \
        --distpath ../dist \
        --workpath ../build \
        main.py
