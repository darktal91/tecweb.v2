#!/usr/bin/perl

use strict;
use warnings;
use CGI;
use CGI::Session();
use CGI::Carp qw(fatalsToBrowser);
use XML::LibXML;
use HTML::Template;

#variabili
my $cgi = new CGI;
my $templatePage = "template/page.tmpl";
my $templateHeader = "template/header.tmpl";
my $templateFooter = "template/footer.tmpl";
my $templateContent= "template/bodies/commenti.tmpl";

## Controllo sessione
my $session = CGI::Session->load();
my $sessionname = $session->param(-name => 'utente');

#creo il template
my $temp = HTML::Template->new(filename=>$templatePage);
$temp->param(HEADER=>qq/<TMPL_INCLUDE name = "$templateHeader">/);
$temp->param(PATH=>"<a href=\"index.cgi\">Home</a> >> Commenti");
$temp->param(CONTENUTO=>qq/<TMPL_INCLUDE name = "$templateContent">/);
$temp->param(FOOTER=>qq/<TMPL_INCLUDE name = "$templateFooter">/);

#setto i valori template per gestire il box di login e il menu
my $user = 0;
my $admin = 0;
my $referrer = "";
if ($sessionname ne "") {
  $user = $sessionname;
  if ($sessionname == "admin") {
    $admin = 1;
  }
}
else { #l'utente non è loggato
  $referrer = "commenti.cgi";
}