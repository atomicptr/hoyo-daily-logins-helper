.PHONY: build

build:
	python setup.py bdist_wheel

install: build
	python -m pip install dist/hoyo_daily_logins_helper-*.whl --force-reinstall

clean:
	rm -rf build dist hoyo_daily_logins_helper.egg-info

upload: clean build
	python -m twine upload dist/hoyo_daily_logins_helper-*.whl