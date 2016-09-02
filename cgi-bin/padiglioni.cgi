#!/usr/bin/perl
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use XML::LibXML;
use CGI::Session();
use Encode;
use HTML::Template;

## creazione ed inizializzazione delle variabili private

my $page = new CGI;
my $templatePage = "template/page.tmpl";
my $templateHeader = "template/header.tmpl";
my $templateFooter = "template/footer.tmpl";
my $templateContent= "template/bodies/padiglioni.tmpl";

# interazione con XML
my $filedati = "../data/padiglioni/padiglioni.xml";
my $parser = XML::LibXML -> new(); #creo il parser
#apertura file
my $doc = $parser->parse_file($filedati) || die("Operazione di parsificazione fallita");
#leggo la radice
my $root = $doc->getDocumentElement || die("Accesso alla radice fallita");


# Controllo sessione
my $session = CGI::Session->load();
my $sessionname = $session->param('utente');

# Inizializzo errori
my $errori = 0;
my $strerr = "";

my $user=0;
my $admin=0;
my $referrer = "";
if ($sessionname ne "") {
  $user=$sessionname;
  if($sessionname eq "admin"){
    $admin=1;
  }
}
else {
  $referrer = "padiglioni.cgi";
}

#creo il template
my $temp = HTML::Template->new(filename=>$templatePage, die_on_bad_params => 0);
$temp->param(HEADER=>qq/<TMPL_INCLUDE name = "$templateHeader">/);
$temp->param(PATH=>"<a href=\"index.cgi\">Home</a> >> Padiglioni");
$temp->param(CONTENUTO=>qq/<TMPL_INCLUDE name = "$templateContent">/);
$temp->param(FOOTER=>qq/<TMPL_INCLUDE name = "$templateFooter">/);
$temp->param(UTENTE=>$user);
$temp->param(ADMIN=>$admin);
$temp->param(RIFE=>$referrer);
my $template = new HTML::Template(scalarref => \$temp->output(), die_on_bad_params => 0);
$template->param(PAGE => "Padiglioni");
$template->param(KEYWORD => "padiglioni, mappa, EmpireCon, fiera, Impero, Star Wars, Convention");
$template->param(ADMIN=>$admin);


my $results = $root->findnodes("//padiglione");
my @nord = @est = @sud = @ovest = ();
my $n = $e = $s = $o = 0;
foreach ($results->get_nodelist) {
  my $nome = $_->findvalue('nome');
  my $settore = $_->findvalue('settore');
  if ($settore eq "Nord") {
    $nord[$n]{NOME} = $nome;
    $n += 1;
  }
  elsif ($settore eq "Est") {
    $est[$e]{NOME} = $nome;
    $e += 1;
  }
  elsif ($settore eq "Sud") {
    $sud[$s]{NOME} = $nome;
    $s += 1;
  }
  else {
    $ovest[$o]{NOME} = $nome;
    $o += 1;
  }
}
$template->param(NORD=> \@nord);
$template->param(EST=> \@est);
$template->param(SUD=> \@sud);
$template->param(OVEST=> \@ovest);

HTML::Template->config(utf8 => 1);
print "Content-Type: text/html\n\n", $template->output;
