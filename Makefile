
TAG=$(shell git describe --tags)

build:	
	pyinstaller src/main.py --name "sensei" --icon "logo.ico" --noconfirm --noconsole \
	--add-data default_config.toml;. \
	--add-data img;img

zip: build
	cd dist && 7z a "sensei-$(TAG).zip" sensei

upload: zip


.PHONY: build