
TAG=$(shell git describe --tags)

BUILD_OPTS=--icon "logo.ico" --noconfirm  \
					 --add-data default_config.toml;. \
					 --add-data version.txt;. \
					 --add-data Roboto-Regular.ttf;. \
					 --add-data logo.png;. \
					 --add-data logo.ico;. \
					 --add-data img;img \
					 --add-data sound;sound \
					 --uac-admin

version:
	echo $(TAG) > version.txt
	sed -i '/#define/ s/MyAppVersion .*/MyAppVersion \"$(TAG)\"/' .\setup.iss
	sed -i '/OutputBaseFilename=/ s/OutputBaseFilename=.*/OutputBaseFilename=sensei-$(TAG)/' .\setup.iss

debug: version
	pyinstaller src/main.py --name "sensei-debug" $(BUILD_OPTS)

build: version
	pyinstaller src/main.py --name "sensei" --noconsole $(BUILD_OPTS)

installer: build
	iscc setup.iss

zip: build
	cd dist && 7z a "sensei-$(TAG).zip" sensei


.PHONY: installer