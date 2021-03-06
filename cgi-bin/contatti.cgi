#!/usr/bin/perl

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Session();
use HTML::Template;

# Creazione ed inizializzazione delle variabili private

my $page = new CGI;
my $templatePage = "template/page.tmpl";
my $templateHeader = "template/header.tmpl";
my $templateFooter = "template/footer.tmpl";
my $templateContent= "template/bodies/contatti.tmpl";

## Controllo sessione
my $session = CGI::Session->load();
my $sessionname = $session->param('utente');

## Variabile discriminante
my $user=0;
my $admin=0;
if ($sessionname ne "") {
  $user=$sessionname;
  if($sessionname eq "admin"){
    $admin=1;
  }
}
else {
  $referrer = "contatti.cgi";
}

# passo i parametri al template
my $template = HTML::Template->new(filename=>$templatePage);
$template->param(HEADER=>qq/<TMPL_INCLUDE name = "$templateHeader">/);
my $home="index.cgi";
$template->param(PATH=>"<a href=\"$home\">Home</a> >> Contatti");
$template->param(UTENTE=>$user);
$template->param(ADMIN=>$admin);
$template->param(RIFE=>$referrer);
$template->param(CONTENUTO=>qq/<TMPL_INCLUDE name = "$templateContent">/);
$template->param(FOOTER=>qq/<TMPL_INCLUDE name = "$templateFooter">/);
#compilazione template
my $tempF = new  HTML::Template(scalarref => \$template->output());
$tempF->param(PAGE => "Contatti");
$tempF->param(KEYWORD => "Contatti, EmpireCon, fiera, Impero, Empire, convention, Star Wars");

HTML::Template->config(utf8 => 1);
print "Content-Type: text/html\n\n", $tempF->output;
