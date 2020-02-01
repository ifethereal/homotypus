PY ?= python
PELICAN ?= pelican
PELICANOPTS =
PORT ?= 8000
SERVER ?= 0.0.0.0

BASEDIR = $(CURDIR)
INPUTDIR = $(BASEDIR)/content
OUTPUTDIR = $(BASEDIR)/output
CONFFILE = $(BASEDIR)/settings.py

# https://stackoverflow.com/a/39451692
ifeq ($(OS), Windows_NT)
	# https://stackoverflow.com/a/2469512
	SASS ?= cmd //C sass.bat

	# https://stackoverflow.com/a/49115945
	OPEN_URL ?= rundll32 url.dll,FileProtocolHandler
else
	SASS ?= sass
	OPEN_URL ?= open
endif
SASSOPTS ?= --embed-source-map
SASSIN = $(BASEDIR)/extra/homotypus.scss
SASSOUT = $(BASEDIR)/theme/static/css/homotypus.css

DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

RELATIVE ?= 0
ifeq ($(RELATIVE), 1)
	PELICANOPTS += --relative-urls
endif

help: info
	@echo -e \
	'Usage:\n'\
	'   make run [PORT=8000]          [re]generate, serve, and open site\n'\
	'   make fresh [PORT=8000]        regenerate, serve, and open site\n'\
	'   make html                     [re]generate the web site\n'\
	'   make css                      [re]generate just the CSS\n'\
	'   make clean                    remove the generated files\n'\
	'   make regenerate               regenerate files upon modification\n'\
	'   make serve [PORT=8000]        serve site at http://localhost:8000\n'\
	'   make serve-global [SERVER=0.0.0.0]\n'\
	'                                 serve (as root) to $(SERVER):80\n'\
	'   make devserver [PORT=8000]    serve and regenerate together\n\n'\
	'Set the DEBUG variable to 1 to enable debugging, e.g. make DEBUG=1 html\n'\
	'Set the RELATIVE variable to 1 to enable relative urls\n'

info:
ifeq ($(DEBUG), 1)
	@echo -e \
	'Makefile for Homotypus\n\n'\
	'Content directory:        $(INPUTDIR)\n'\
	'Output directory:         $(OUTPUTDIR)\n'\
	'Pelican settings file:    $(CONFFILE)\n\n'
endif

fresh: | clean run

# https://stackoverflow.com/questions/3004811
# /how-do-you-run-multiple-programs-in-parallel-from-a-bash-script
# /5553774#comment74281615_5553774
run: | info html
	@(sleep 1; $(OPEN_URL) "http://localhost:$(PORT)/") & $(MAKE) serve \
	&& kill $!

html: css | info
	@echo Generating HTML using Pelican into output directory
	@$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

clean:
	@[ ! -d $(OUTPUTDIR) ] || (\
		echo Removing output directory; \
		rm -rf $(OUTPUTDIR) \
	)
	@[ ! -f $(SASSOUT) ] || (\
		echo Removing generated CSS files; \
		rm -rf $(SASSOUT) \
	)

regenerate: css | info
	$(PELICAN) -r $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

serve: css | info
	@echo Serving site with Pelican
	@$(PELICAN) -l $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS) \
	-p $(PORT)

serve-global: css
	$(PELICAN) -l $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS) \
	-p $(PORT) -b $(SERVER)

devserver: css | info
	$(PELICAN) -lr $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS) \
	-p $(PORT)

css: $(SASSOUT) | info

$(SASSOUT): $(SASSIN)
	@echo Generating CSS files using Sass
	@$(SASS) $(SASSOPTS) $(SASSIN) $(SASSOUT)

# Original Sass file won't have any process that generates it, so make an empty
# rule for it rather than let make search through implicit rules
$(SASSIN): ;

.PHONY: html help clean regenerate serve serve-global devserver css info \
	fresh run
