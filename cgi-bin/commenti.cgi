#!/usr/bin/perl

use strict;
use warnings;
use CGI;
use CGI::Session();
use CGI::Carp qw(fatalsToBrowser);
use XML::LibXML;
use HTML::Template;

#variabili
my $page = new CGI;
my $templatePage = "template/page.tmpl";
my $templateHeader = "template/header.tmpl";
my $templateFooter = "template/footer.tmpl";
my $templateContent= "template/bodies/commenti.tmpl";

## Controllo sessione
my $session = CGI::Session->load();
my $sessionname = $session->param(-name => 'utente');

#interazione con XML
my $filedati = "../data/commenti/commenti.xml";
my $parser = XML::LibXML -> new(); #creo il parser
#apertura file
my $doc = $parser->parse_file($filedati) || die("Operazione di parsificazione fallita");
#leggo la radice
my $root = $doc->getDocumentElement || die("Accesso alla radice fallita");

#setto i valori template per gestire il box di login e il menu
my $user = 0;
my $admin = 0;
my $auth = 0;
my $referrer = "";
if ($sessionname ne "") {
  $user = $sessionname;
  $auth = 1;
  if ($sessionname == "admin") {
    $admin = 1;
  }
  
  #INIZIO PARTE MODIFICA
  #se operation=insert => inserimento commento
  #se operation=delete => cancellazione commento (admin + owner)
  my $operation = "";
  $operation = $page->param("operation");
  if ($operation eq "insert") { #inserimento di un commento
    # prendo datetime del momento dell'inserimento
    (my $sec, my $min, my $hour, my $day, my $mon, my $year, my @rest) = localtime(time);
    $year += 1900; #normalizzo l'anno
    #aggiungo eventuali 0 se <10 per normalizzare
    $sec = sprintf("%02d", $sec);
    $min = sprintf("%02d", $min);
    $hour = sprintf("%02d", $hour);
    $day = sprintf("%02d", $day);
    $mon = sprintf("%02d", $mon+1);
    my $curdate = "$year-$mon-$day" . "T$hour:$min:$sec";
    my $comment = $page->param("testo");
    
    #inserimento vero e proprio
    my $frammento = "\t<commento>
\t\t<username>$user</username>
\t\t<datetime>$curdate</datetime>
\t\t<testo>$comment</testo>
\t</commento>\n";
    
    my $newnodo = $parser->parse_balanced_chunk($frammento) || die("Frammento non ben formato");
    $root->appendChild($newnodo) || die("Non riesco a trovare il padre");
    $doc->toFile($filedati);
    #il nodo è stato inserito
    #eseguo il redirect su commenti.cgi per svuotare le variabili post
    print $page->header(-location => "commenti.cgi");
  }
  elsif ($operation eq "delete") { #cancellazione di un commento
    my $owner = $page->param("username");
    my $dt = $page->param("datetime");
    if ($owner ne $user && $user ne "admin") { #non posso cancellare
      #errore
    }
    else { #cancello
      my $node = $root->findnodes("//commento[username='$owner' and datetime='$dt']")->get_node(1) or die("Fallimento nel recupero del nodo per l'eliminazione");
      $node->parentNode->removeChild($node) or die("Fallimento di unbind");
      $doc->toFile($filedati) or die("Fallimento in scrittura");
      print $page->header(-location => "commenti.cgi");
    }
  }
  
}
else { #l'utente non è loggato
  $referrer = "commenti.cgi";
}

#RECUPERO TUTTI I COMMENTI
my $results = $root->findnodes('//commento');
my $context = $results->get_nodelist;
#butto tutto in un array
my @commenti = ();
my %row;
my $i=0;
foreach ($results->get_nodelist) {
  $row{"USERNAME"} = $_->findvalue('username');
  $row{"DATETIME"} = $_->findvalue('datetime');
  $row{"TESTO"} = $_->findvalue('testo');
  if ($row{"USERNAME"} eq $user || $user eq "admin") {
    $row{"DEL"} = "1";
  }
  else { 
    $row{"DEL"} = "0";
  }
  $row{"NORMDT"} = normalize_datetime($row{"DATETIME"});
  foreach my $key (keys %row) {
    $commenti[$i]{$key}=$row{$key};
  }
  $i += 1;
}

#ordino l'array per date discendenti
my @sortedcomments = ();
@sortedcomments =  sort { lc($b->{DATETIME}) cmp lc($a->{DATETIME}) } @commenti;



#creo il template
my $temp = HTML::Template->new(filename=>$templatePage, die_on_bad_params => 0);
$temp->param(HEADER=>qq/<TMPL_INCLUDE name = "$templateHeader">/);
$temp->param(PATH=>"<a href=\"index.cgi\">Home</a> >> Commenti");
$temp->param(CONTENUTO=>qq/<TMPL_INCLUDE name = "$templateContent">/);
$temp->param(FOOTER=>qq/<TMPL_INCLUDE name = "$templateFooter">/);
$temp->param(UTENTE=>$user);
$temp->param(ADMIN=>$admin);
$temp->param(RIFE=>$referrer);

#compilazione template
my $template = new HTML::Template(scalarref => \$temp->output(), die_on_bad_params => 0);
$template->param(PAGE => "Commenti");
$template->param(KEYWORD => "commenti, EmpireCon, fiera, Impero, Star Wars, Convention");
$template->param(COMMENTI=> \@sortedcomments);
$template->param(AUTENTICATO=>$auth);

HTML::Template->config(utf8=>1);
print "Content-Type: text/html\n\n", $template->output;

sub normalize_datetime {
  my $dt=@_[0];
  $dt =~ (/(\d{4})\-(\d{2})\-(\d{2})T(\d{2}\:\d{2}\:\d{2})/);
  return $3 . "/" . $2 . "/" . $1 . " alle " . $4;
}
