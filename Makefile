PYTHON=/usr/bin/python2.6
DESTDIR=/
BUILDIR=$(CURDIR)/debian/seriesfinale
PROJECT=seriesfinale
PO_DIR=po
LINGUAS=$(shell cat $(PO_DIR)/LINGUAS)
RESOURCES_DIR=data

all:
	@echo "make source   - Create source package"
	@echo "make install  - Install on local system"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean    - Get rid of scratch and byte files"

po/$(PROJECT).pot:
	cd $(PO_DIR); intltool-update -p -g $(PROJECT)

update-po: $(PO_DIR)/$(PROJECT).pot
	cd $(PO_DIR); intltool-update -r -g $(PROJECT)

%.mo : %.po
	@langname=`basename $(<) .po`; \
	dirname=locale/$$langname/LC_MESSAGES/; \
	echo Generating $$dirname/$(PROJECT).mo; \
	mkdir -p $$dirname; \
	msgfmt $< -o $$dirname/$(PROJECT).mo; \

generate-mo: $(patsubst %,$(PO_DIR)/%.mo,$(LINGUAS))

$(RESOURCES_DIR)/$(PROJECT).desktop: $(RESOURCES_DIR)/$(PROJECT).desktop.in $(PO_DIR)/*.po
	@intltool-merge -d $(PO_DIR) $(RESOURCES_DIR)/$(PROJECT).desktop.in $(RESOURCES_DIR)/$(PROJECT).desktop

i18n: po/$(PROJECT).pot update-po generate-mo $(RESOURCES_DIR)/$(PROJECT).desktop

source: i18n
	$(PYTHON) setup.py sdist $(COMPILE)

install: i18n
	$(PYTHON) setup.py install --root=$(DESTDIR) $(COMPILE)

deb: i18n
	# build the source package in the parent directory
	# then rename it to project_version.orig.tar.gz
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../ 
	rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
	# build the package
	dpkg-buildpackage -us -uc -rfakeroot -sa

clean:
	$(PYTHON) setup.py clean
	rm -rf build/ locale/ MANIFEST data/seriesfinale.desktop po/seriesfinale.pot
	find . -name '*.py[oc]' -exec rm {} \;
	find . -name '*~' -exec rm {} \;
