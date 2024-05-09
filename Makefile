all: test
	-rm README.md
	make README.md

README.md:
	python3 pallet.py -m -s all > README.md

.PHONY: test
test:
	python3 pallet.py -f test.pallet
