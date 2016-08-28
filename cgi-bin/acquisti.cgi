#!/usr/bin/perl

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use XML::LibXML;
use CGI::Session();
use HTML::Template;
use feature qw(switch);
use Scalar::Util 'looks_like_number';

# $login{"level"} indica il livello di accessibilita' dell'utente ( 0 = non loggato, 1 = utente, 2 = admin)

my $page = new CGI;
my $templatePage = "template/page.tmpl";
my $templateHeader = "template/header.tmpl";
my $templateFooter = "template/footer.tmpl";
my $templateContent= "template/bodies/acquisti.tmpl";
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
  $referrer = "acquisti.cgi";
}

my $acquista   = $page->param('acquista');
my $conferma = $page->param('conferma');


sub get_info_biglietti {
  my @res = ();
  
  foreach my $tipologia ($doc->findnodes('//tipologia')) {
    my $info = {
      id          => $tipologia->{id}, 
      prezzo      => $tipologia->{prezzo},
      descrizione => $tipologia->{descrizione},
      quantita    => defined($page->param($tipologia->{id})) ? $page->param($tipologia->{id}) : 0
    };
    push @res, $info;
  }
  return \@res;
}

sub get_current_datatime {
    (my $sec, my $min, my $hour, my $day, my $mon, my $year, my @rest) = localtime(time);
    $year += 1900;
    $sec = sprintf("%02d", $sec);
    $min = sprintf("%02d", $min);
    $hour = sprintf("%02d", $hour);
    $day = sprintf("%02d", $day);
    $mon = sprintf("%02d", $mon+1);
    return "$year-$mon-$day" . "T$hour:$min:$sec";
}

sub remove_empty_ticket_types {
  my $tt = shift @_;
  my @ref = grep { $_->{quantita} >0 } @{$tt};
  return \@ref;
}

sub chk_dati {
  my $arr_ref = shift @_;
  my $res = 1;
  foreach my $ele (@{$arr_ref}) {
    if (!(looks_like_number($ele->{quantita})) || ($ele->{quantita} < 0)) {
      $res = 0;
    }
  }
  return $res;
}

sub conta_biglietti_acquistati {
  my $arr_ref = shift @_;
  my $res = 0;
  foreach my $ele (@{$arr_ref}) {
    if (looks_like_number($ele->{quantita})) {
      $res += $ele->{quantita};
    }
  }
  return $res;
}



my $infotipi = get_info_biglietti();
my $errqta = 0;
my $zerobiglietti = 0;

if ($acquista) {
  $zerobiglietti = (conta_biglietti_acquistati($infotipi) > 0 ) ? 0 : 1;
}


if ($conferma) {
  if (chk_dati($infotipi) && (!$zerobiglietti)) {
    my $oracorrente = get_current_datatime();
    
    $infotipi = remove_empty_ticket_types($infotipi);
    
    foreach my $ele (@{$infotipi}) {
      my $frammento = qq{\t<acquisto username="$sessionname" datatime="$oracorrente">$ele->{quantita}</acquisto>\n\t};
      my $newnodo = $parser->parse_balanced_chunk($frammento) || die("Frammento non ben formato");
      my $query = '//tipologia[@id="' . $ele->{id} . '"]';
      my $nodotipologia = $doc->findnodes($query)->[0];
      $nodotipologia->appendChild($newnodo) || die ("non riesco a trovare il padre");
    }
    $doc->toFile($fileacquisti);
  } else { #dati probabilmente manomessi
    $errqta = 1;
    $acquista = 0;
    $conferma = 0;
  }
}

if ($acquista ) {
  if (!chk_dati($infotipi)){ # ... || $zerobiglietti
    $errqta = 1;
    $acquista = 0;
  } else {
    if (!$zerobiglietti) {
      $infotipi = remove_empty_ticket_types($infotipi);
    }
  }
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
$tempF->param(INFOBIGLIETTI=>$infotipi);
$tempF->param(AUTENTICATO=>$auth);

$tempF->param(ACQUISTA=>$acquista);
$tempF->param(CONFERMA=>$conferma);
$tempF->param(ERRQTA=>$errqta);
$tempF->param(ZEROBIGLIETTI=>$zerobiglietti);

HTML::Template->config(utf8 => 1);
print "Content-Type: text/html\n\n", $tempF->output;
