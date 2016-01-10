define RELEASE_CHECKLIST
RELEASE CHECKLIST:
* Update documentation (then run pre-release again)
* Commit changes
* Update version number
* make release
endef
export RELEASE_CHECKLIST

all:
	echo "Valid targets are 'install', 'pre-release', 'release' and 'test'"

clean:
	rm -rf build dist hipcat.egg-info
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

install:
	pip install -r requirements.txt

pre-release:
	pandoc --from=markdown --to=rst --output=README.rst README.md
	@echo "$$RELEASE_CHECKLIST"

release:
	@if git diff --quiet --cached; then\
		python setup.py sdist bdist_wheel;\
	else\
		echo 'COMMIT YOUR CHANGES BEFORE RELEASING'; exit 1;\
	fi

test:
	tox -r

.PHONY: all install pre-release release test
