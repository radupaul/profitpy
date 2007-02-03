pyrcc = pyrcc4
pyrccopt = -o
images := `find ./images -name "*.png"|sort|cut -b 3-`
rcsrc = profit.qrc
rcout = rc.py


.PHONY : all clean $(rcout) widgets


all : widgets


full : all $(rcout)


clean :
	rm -f -R *.pyc
	rm -f -R *.pyo
	cd widgets && $(MAKE) clean


widgets :
	cd widgets && $(MAKE)


$(rcout) :
	@rm -f $(rcsrc)
	@echo '<!DOCTYPE RCC><RCC version="1.0">' >> $(rcsrc)
	@echo '<qresource>' >> $(rcsrc)
	@for file in $(wordlist 1,$(words $(images)),$(images)); \
		do echo "<file>$${file}</file>" >> $(rcsrc); done
	@echo '</qresource>' >> $(rcsrc)
	@echo '</RCC>' >> $(rcsrc)
	$(pyrcc) $(pyrccopt) $@ $(rcsrc)
