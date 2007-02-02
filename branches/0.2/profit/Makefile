pyuic = pyuic4
pyuicopt = -x -o
pyrcc = pyrcc4
pyrccopt = -o
objects := $(addsuffix .py, $(basename $(wildcard *.ui)))
images := `find ./images -name "*.png"|sort|cut -b 3-`
rctmp = profit.rc
rcfile = profitrc.py


.PHONY : all clean profitrc.py


all : $(objects)


full : all profitrc.py


clean :
	rm -f $(objects)
	rm -f *.pyc
	rm -f *.pyo
	rm -f $(rctmp)
	rm -f $(rcfile)

$(objects) : %.py: %.ui
	$(pyuic) $(pyuicopt) $@ $< 


$(rcfile) :
	@rm -f $(rctmp)
	@echo '<!DOCTYPE RCC><RCC version="1.0">' >> $(rctmp)
	@echo '<qresource>' >> $(rctmp)
	@for file in $(wordlist 1,$(words $(images)),$(images)); \
		do echo "<file>$${file}</file>" >> $(rctmp); done
	@echo '</qresource>' >> $(rctmp)
	@echo '</RCC>' >> $(rctmp)
	$(pyrcc) $(pyrccopt) $@ $(rctmp)
	@rm -f $(rctmp)
