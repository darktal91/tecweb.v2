#!/usr/bin/perl

# importazione dei moduli necessari
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use XML::LibXML;
use CGI::Session();
use HTML::Template;
use Encode;

# creazione delle variabili dello script

my $page = new CGI;
my $templatePage = "template/page.tmpl";
my $templateHeader = "template/header.tmpl";
my $templateFooter = "template/footer.tmpl";
my $templateContent= "template/bodies/controlloRicavi.tmpl";

## Controllo sessione
my $session = CGI::Session->load();
my $sessionname = $session->param('utente');

#interazione con XML
my $fileacquisti = "../data/acquisti/acquisti.xml";

my $parser = XML::LibXML -> new();
#apro il file
my $doc = $parser -> parse_file($fileacquisti) || die ("operazione di parsificazione fallita.");
#leggo la radice
my $root = $doc->getDocumentElement || die("Accesso alla radice fallito.");


my $user = 0;
my $admin = 0;
my $auth = 0;
my $referrer = "";
if ($sessionname ne "") {
  $user = $sessionname;
  $auth = 1;
  if ($sessionname eq "admin") {
    $admin = 1;
  }  
} else {
  $referrer = "controlloRicavi.cgi";
}

  my @inforicavi = ();
  
  my $ntotalebiglietti = 0;
  my $ricavototale = 0;
  
  foreach my $tipologia ($doc->findnodes('//tipologia')) {
    my $ricavotipo = 0;
    my $nbigliettitipo = 0;
    my $prezzotipo = $tipologia->getAttribute(prezzo);
  
    foreach my $acquisto ($tipologia->findnodes(qq(./acquisto))){
      $nbigliettitipo += $acquisto->findvalue('./text()');
    }
    
    $ntotalebiglietti += $nbigliettitipo;
    $ricavotipo = $nbigliettitipo * $prezzotipo;
    $ricavototale += $ricavotipo;
    
    my $info = {
      id          => $tipologia->getAttribute(id), 
      descrizione => $tipologia->getAttribute(descrizione),
      prezzo      => $prezzotipo,
      quantita    => $nbigliettitipo,
      ricavo      => $ricavotipo
    };
    push @inforicavi,$info;
  }



# preparo la pagina usando i vari template
my $template = HTML::Template->new(filename=>$templatePage);
$template->param(HEADER=>qq/<TMPL_INCLUDE name = "$templateHeader">/);
my $home="index.cgi";
$template->param(PATH=>"<a href=\"$home\">Home</a> >> Controllo Ricavi");
$template->param(UTENTE=>$user);
$template->param(ADMIN=>$admin);
$template->param(CONTENUTO=>qq/<TMPL_INCLUDE name = "$templateContent">/);
$template->param(FOOTER=>qq/<TMPL_INCLUDE name = "$templateFooter">/);
#compilazione template
my $tempF = new  HTML::Template(scalarref => \$template->output());
$tempF->param(PAGE => "Controllo Ricavi");
$tempF->param(KEYWORD => "ricavi, EmpireCon, fiera, Rovigo, Impero,Empire");
$tempF->param(ADMIN => $admin);
$tempF->param(INFORICAVI=>\@inforicavi);
$tempF->param(NTOTALEBIGLIETTI=>$ntotalebiglietti);
$tempF->param(RICAVOTOTALE=>$ricavototale);
$tempF->param(AUTENTICATO=>$auth);

HTML::Template->config(utf8 => 1);
print "Content-Type: text/html\n\n", $tempF->output;
