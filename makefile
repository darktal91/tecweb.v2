build-clean: clean mk-dir cp-xsd cp-xsl cp-cgi cp-html
	@echo "Copying clean xml data files.."
	@cp build/files/acquisti/*.xml build/data/acquisti/
	@cp build/files/commenti/*.xml build/data/commenti/
	@cp build/files/eventi/*.xml build/data/eventi/
	@cp build/files/padiglioni/*.xml build/data/padiglioni/
	@cp build/files/utenti/*.xml build/data/utenti/
	@echo "Clean build created."


build-dirty: clean mk-dir cp-xsd cp-xsl cp-cgi cp-html
	@echo "Copying repo xml data files.."
	@cp data/acquisti/*.xml build/data/acquisti/
	@cp data/commenti/*.xml build/data/commenti/
	@cp data/eventi/*.xml build/data/eventi/
	@cp data/padiglioni/*.xml build/data/padiglioni/
	@cp data/utenti/*.xml build/data/utenti/
	@echo "Dirty build created."

cp-cgi:
	@echo "Copying cgi-bin.."
	@cp -r cgi-bin build/
	@echo "Done."

cp-html:
	@echo "Copying public_html.."
	@cp -r public_html build/
	@echo "Done."

mk-dir:
	@echo "Creating directories for data.."
	@mkdir -p build/data
	@mkdir -p build/data/acquisti
	@mkdir -p build/data/commenti
	@mkdir -p build/data/eventi
	@mkdir -p build/data/padiglioni
	@mkdir -p build/data/utenti
	@echo "Done."

cp-xsd:
	@echo "Copying xmlschema files.."
	@cp data/acquisti/*.xsd build/data/acquisti/
	@cp data/commenti/*.xsd build/data/commenti/
	@cp data/eventi/*.xsd build/data/eventi/
	@cp data/padiglioni/*.xsd build/data/padiglioni/
	@cp data/utenti/*.xsd build/data/utenti/
	@echo "Done."

cp-xsl:
	@echo "Copying xsl files.."
	@cp data/acquisti/*.xsl build/data/acquisti/ | true
	@cp data/commenti/*.xsl build/data/commenti/ | true
	@cp data/eventi/*.xsl build/data/eventi/ | true
	@cp data/padiglioni/*.xsl build/data/padiglioni/ | true
	@cp data/utenti/*.xsl build/data/utenti/ | true
	@echo "Done."

clean:
	@echo "Cleaning build dir.."
	@rm -Rf build/cgi-bin build/public_html build/data
	@echo "Done."