
Roundtripper = Roundtripper

all: help

help:
	@echo Targets:
	@echo
	@echo "  clean: remove unneeded files"
	@echo


clean:
	rm -f _gfdepgraph.dot *.hi *.o


Roundtripper: $(Roundtripper).hs
	ghc --make -o $(Roundtripper) $(Roundtripper).hs
