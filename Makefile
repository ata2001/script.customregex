SHELL := /bin/bash

build:
	make clean
	mkdir script.customregex
	for f in $$(git ls-tree --full-tree --name-only -r HEAD); \
		do cp --parents $$f script.customregex/; \
		done
	zip -r script.customregex.zip script.customregex

clean:
	rm -r script.customregex
	rm script.customregex.zip

install:
	rm -r ~/.kodi/addons/script.customregex
	cp -r script.customregex ~/.kodi/addons/
