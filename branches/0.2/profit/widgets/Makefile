pyuic = pyuic4
pyuicopt = -x -o
objects := $(addsuffix .py, $(basename $(wildcard *.ui)))


.PHONY : all clean $(rcout)

all : $(objects)


$(objects) : %.py: %.ui
	$(pyuic) $(pyuicopt) $@ $< 


clean : 
	rm -f $(objects)
	rm -f *.pyc
	rm -f *.pyo
