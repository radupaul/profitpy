pyrcc = pyrcc4
pyrccopt = -o
images := `find ./images -name "*.png"|sort|cut -b 3-`
rctmp = profit.rc
rcfile = rc.py


.PHONY : all clean $(rcfile) widgets


all : widgets


full : all $(rcfile)


clean :
	rm -f -R *.pyc
	rm -f -R *.pyo
	rm -f $(rctmp)
	cd widgets && $(MAKE) clean


widgets :
	cd widgets && $(MAKE)


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
