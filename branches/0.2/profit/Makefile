pyuic = pyuic4
pyuicopt = -x -o
objects := $(addsuffix .py, $(basename $(wildcard *.ui)))

.PHONY : all clean
all : $(objects)

clean :
	rm $(objects)

$(objects) : %.py: %.ui
	$(pyuic) $(pyuicopt) $@ $< 

