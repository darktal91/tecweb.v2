#!/bin/bash

xmllint --noout --schema data/acquisti/acquisti.xsd data/acquisti/acquisti.xml
xmllint --noout --schema data/commenti/commenti.xsd data/commenti/commenti.xml
xmllint --noout --schema data/eventi/eventi.xsd data/eventi/eventi.xml
xmllint --noout --schema data/padiglioni/padiglioni.xsd data/padiglioni/padiglioni.xml
xmllint --noout --schema data/utenti/utenti.xsd data/utenti/utenti.xml
