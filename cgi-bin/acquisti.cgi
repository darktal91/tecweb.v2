#!/usr/bin/perl

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use XML::LibXML;
use CGI::Session();
use HTML::Template;


#print "Content-type: text/html\n\n";

# $login{"level"} indica il livello di accessibilita' dell'utente ( 0 = non loggato, 1 = utente, 2 = admin)

my $page = new CGI;
my $templatePage = "template/page.tmpl";
my $templateHeader = "template/header.tmpl";
my $templateFooter = "template/footer.tmpl";
my $templateContent= "template/bodies/acquisti.tmpl";
$file_acquisti = '../data/acquisti/acquisti.xml';
# $ns_uri  = 'http://www.imperofiere.com';
# $ns_abbr = 'a';

## Controllo sessione
my $session = CGI::Session->load();
my $sessionname = $session->param('utente');

my $user=0;
my $admin=0;
my $referrer = "";
if ($sessionname ne "") {
  $user=$sessionname;
  if($sessionname == "admin"){
    $admin=1;
  }
}
else {
  $referrer = "acquisti.cgi";
}



# #espressioni xpath
# my $ticketTypesXPath = "/${ns_abbr}:acquisti/${ns_abbr}:tipologia/\@id";
# 
# #messaggi errore
# $parsing_err     = "Operazione di parsing fallita";
# $access_root_err = "Impossibile accedere alla radice";
# 
# #creo il parser
# my $parser = XML::LibXML->new();
# 
# #parser del documento
# my $doc = $parser->parse_file($file_acquisti) || die($parsing_err);
# 
# #recupero l'elemento radice
# my $root_acq = $doc->getDocumentElement || die($access_root_err);
# 
# #inserisco il namespace
# $doc->documentElement->setNamespace($ns_uri,$ns_abbr);
# 
# my @tipiBiglietti = $root_acq->findnodes($ticketTypesXPath);
# 
# # foreach my $tipoBiglietti (@tipibiglietto) { print $tipoBiglietti->getValue() ."<br />"; } #http://html-template.sourceforge.net/html_template.html#tmpl_loop
# 
# 
# 
# my @loop_data = ();  # initialize an array to hold your loop
# 
# 
# foreach my $tipoBiglietto ( @tipiBiglietti) {
# 	 my %row_data;  # get a fresh hash for the row data
# 	  # fill in this row
# 	 $row_data{TIPIBIGLIETTI} =  $tipoBiglietto->getValue();
# 	 
# 	 # the crucial step - push a reference to this row into the loop!
# 	 push(@loop_data, \%row_data);
# }

# preparo la pagina usando i vari template
my $template = HTML::Template->new(filename=>$templatePage);
$template->param(HEADER=>qq/<TMPL_INCLUDE name = "$templateHeader">/);
my $home="index.cgi";
$template->param(PATH=>"<a href=\"$home\">Home</a> >> Acquista biglietti");
$template->param(UTENTE=>$user);
$template->param(ADMIN=>$admin);
$template->param(RIFE=>$referrer);
$template->param(CONTENUTO=>qq/<TMPL_INCLUDE name = "$templateContent">/);
# $template->param(LOOP_TIPIBIGLIETTI=>\@loop_data);
$template->param(FOOTER=>qq/<TMPL_INCLUDE name = "$templateFooter">/);
#compilazione template
my $tempF = new  HTML::Template(scalarref => \$template->output());
$tempF->param(PAGE => "Acquista biglietti");
$tempF->param(KEYWORD => "Biglietti, Acquista, EmpireCon, fiera, Rovigo, Impero,Empire");

HTML::Template->config(utf8 => 1);
print "Content-Type: text/html\n\n", $tempF->output;




