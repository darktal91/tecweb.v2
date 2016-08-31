#!/usr/bin/perl

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use XML::LibXML;
use CGI::Session();
use HTML::Template;
use Encode;

# $login{"level"} indica il livello di accessibilita' dell'utente ( 0 = non loggato, 1 = utente, 2 = admin)

my $page = new CGI;
my $templatePage = "template/page.tmpl";
my $templateHeader = "template/header.tmpl";
my $templateFooter = "template/footer.tmpl";
my $templateContent= "template/bodies/bigliettiAcquistati.tmpl";
my $file_acquisti = '../data/acquisti/acquisti.xml';


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

#setto i valori template per gestire il box di login e il menu
my $user=0;
my $admin=0;
my $auth=0;
my $referrer = "";
if ($sessionname ne "") {
  $user=$sessionname;
  $auth = 1;
  if($sessionname == "admin"){
    $admin=1;
  }
}
else {
  $referrer = "bigliettiAcquistati.cgi";
}


my @ids = ();
#my @descriptions = ();
my @prices = ();
my @ntickets = ();
my @datatime = ();
my @numdatatime = ();
my @nacquisti = ();
my $nacquistitot = 0;


foreach my $tipologia ($doc->findnodes(qq(//acquisto[\@username="$sessionname"]/..))) {
  push @ids, encode('UTF-8',$tipologia->getAttribute(id),  Encode::FB_CROAK);
#  push @descriptions, encode('UTF-8',$tipologia->getAttribute(descrizione)),  Encode::FB_CROAK);
  push @prices, $tipologia->getAttribute(prezzo);
    
  my $count = 0;
  
  foreach my $acquisto ($tipologia->findnodes(qq(./acquisto[\@username="$sessionname"]))) {
    push @datatime,$acquisto->getAttribute(datatime);
    my $acq = $acquisto->findvalue('./text()');
    $nacquistitot += $acq;
    push @nacquisti, $acq;
    $count++;
  }
  
  push @numdatatime, $count;
  
}

my @infoacquisti = ();


while (@ids){
  my %row_data;
  $row_data{ID} = shift @ids;
  #$row_data{DESCRIZIONE} = shift @descriptions;
  $row_data{PREZZO} = shift @prices;
#   $row_data{NUMDATATIME} = shift @numdatatime;
  my $ndt = shift @numdatatime;
  
  
  my @info_datatime = ();
  
  for (my $i = 0; $i < $ndt; $i++)
  {
    my %nested_row_data;
    $nested_row_data{NACQUISTI} = shift @nacquisti;
    $nested_row_data{DATATIME} = shift @datatime;
    push(@info_datatime, \%nested_row_data);
  }
  $row_data{INFO_DATATIME} = \@info_datatime;
  # The crucial step - push a reference to this row into the loop!
  push(@infoacquisti, \%row_data);
}

# preparo la pagina usando i vari template
my $template = HTML::Template->new(filename=>$templatePage);
$template->param(HEADER=>qq/<TMPL_INCLUDE name = "$templateHeader">/);
my $home="index.cgi";
$template->param(PATH=>"<a href=\"$home\">Home</a> >> Acquista biglietti");
$template->param(UTENTE=>$user);
$template->param(ADMIN=>$admin);
$template->param(RIFE=>$referrer);
$template->param(CONTENUTO=>qq/<TMPL_INCLUDE name = "$templateContent">/);
$template->param(FOOTER=>qq/<TMPL_INCLUDE name = "$templateFooter">/);
#compilazione template
my $tempF = new  HTML::Template(scalarref => \$template->output());
$tempF->param(PAGE => "Acquista biglietti");
$tempF->param(KEYWORD => "Biglietti, Acquista, EmpireCon, fiera, Rovigo, Impero,Empire");
$tempF->param(INFOACQUISTI=>\@infoacquisti);
$tempF->param(AUTENTICATO=>$auth);
$tempF->param(NACQUISTITOT=>$nacquistitot);


HTML::Template->config(utf8 => 1);
print "Content-Type: text/html\n\n", $tempF->output;

