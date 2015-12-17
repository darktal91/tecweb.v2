#!/usr/bin/perl

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Session();
use HTML::Template;

# creo e inizializzo i template
$page = new CGI;
my $page = new CGI;
my $templatePage = "template/page.tmpl";
my $templateHeader = "template/header.tmpl";
my $templateFooter = "template/footer.tmpl";
my $templateContent= "template/bodies/index.tmpl";

## Controllo sessione
my $session = CGI::Session->load();
my $sessionname = $session->param('utente');

my $user=0;
my $admin=0;
my $referrer = "";
if ($sessionname ne "") {
  $user=1;
  if($sessionname == "admin"){
    $admin=1;
  }
}
else {
  $referrer = "index.cgi";
}

# passo i parametri ai template e stampo la pagina
my $template = HTML::Template->new(filename=>$templatePage);
$template->param(HEADER=>qq/<TMPL_INCLUDE name = "$templateHeader">/);
$template->param(PATH=>"Home");
$template->param(UTENTE=>$user);
$template->param(ADMIN=>$admin);
$template->param(RIFE=>$referrer);
$template->param(CONTENUTO=>qq/<TMPL_INCLUDE name = "$templateContent">/);
$template->param(FOOTER=>qq/<TMPL_INCLUDE name = "$templateFooter">/);
#compilo template
my $tempF = new  HTML::Template(scalarref => \$template->output());
$tempF->param(PAGE => "Index");
$tempF->param(KEYWORD => "Index, home, EmpireCon, fiera, Rovigo, Impero, Empire");

HTML::Template->config(utf8 => 1);
print "Content-Type: text/html\n\n", $tempF->output;