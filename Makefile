.PHONY: build

build: clean
	python -m build --sdist --wheel --outdir dist/ .

install: build
	python -m pip install dist/hoyo_daily_logins_helper-*.whl --force-reinstall

clean:
	rm -rf build dist hoyo_daily_logins_helper.egg-info
