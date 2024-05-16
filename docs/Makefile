# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: clean-html
clean-html:
	rm -rf "$(SOURCEDIR)/_autosummary/"*
	rm -rf "$(BUILDDIR)/$(BUILDER)"
	rm -rf "$(BUILDDIR)/doctrees"

.PHONY: clean-builder
clean-builder:
	rm -rf "$(SOURCEDIR)/_autosummary/"*
	rm -rf "$(BUILDDIR)/$(BUILDER)"


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@if [ "$@" = "html" ] || [ "$@" = "dirhtml" ] || [ "$@" = "singlehtml" ] || [ "$@" = "htmlhelp" ]  || [ "$@" = "qthelp" ]; then \
		$(MAKE) clean-html BUILDER=$@; \
	else \
		$(MAKE) clean-builder BUILDER=$@; \
	fi
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
