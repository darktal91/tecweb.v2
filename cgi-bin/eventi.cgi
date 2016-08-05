#!/usr/bin/perl

# importazione dei moduli necessari
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use XML::LibXML;
use CGI::Session();
use HTML::Template;
use Encode;
use MIME::Base64;

# creazione delle variabili dello script
my $page = new CGI;
my $templatePage = "template/page.tmpl";
my $templateHeader = "template/header.tmpl";
my $templateFooter = "template/footer.tmpl";
my $templateContent= "template/bodies/eventi.tmpl";

# interazione con XML
my $filedati = "../data/eventi/eventi.xml";
my $parser = XML::LibXML -> new(); #creo il parser
#apertura file
my $doc = $parser->parse_file($filedati) || die("Operazione di parsificazione fallita");
#leggo la radice
my $root = $doc->getDocumentElement || die("Accesso alla radice fallita");


## Controllo sessione
my $session = CGI::Session->load();
my $sessionname = $session->param('utente');

# inizializzo errori
$errori = 0;
$strerr = "";

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
  $referrer = "eventi.cgi";
}

#creo il template
my $temp = HTML::Template->new(filename=>$templatePage, die_on_bad_params => 0);
$temp->param(HEADER=>qq/<TMPL_INCLUDE name = "$templateHeader">/);
$temp->param(PATH=>"<a href=\"index.cgi\">Home</a> >> Eventi");
$temp->param(CONTENUTO=>qq/<TMPL_INCLUDE name = "$templateContent">/);
$temp->param(FOOTER=>qq/<TMPL_INCLUDE name = "$templateFooter">/);
$temp->param(UTENTE=>$user);
$temp->param(ADMIN=>$admin);
$temp->param(RIFE=>$referrer);


#eventuale modifica
#  0/null -> visualizzazione
#  1 -> modifica
#      action=insert -> inserimento
#      action=Modifica -> modifica
#      action=Elimina -> eliminazione
my $mod = $page->param("mod");
my $action = $page->param("action");

if($mod == 1 and $action ne "Elimina") {  #parte di modifica/nuovo
  if($admin == 1) {
    my $id = $page->param("id");
    
    # RECUPERO I PADIGLIONI DA XML
    my $filepad = "../data/padiglioni/padiglioni.xml";
    my $parserpad = XML::LibXML -> new(); #creo il parser
    #apertura file
    my $docpad = $parserpad->parse_file($filepad) || die("Operazione di parsificazione padiglioni fallita");
    #leggo la radice
    my $rootpad = $docpad->getDocumentElement || die("Accesso alla radice padiglioni fallita");
    my $resultspad = $rootpad->findnodes('//padiglione');
    
    if ($action eq "" or $action eq "Nuovo") {
      #sono in azione di nuovo evento
      my $submit = $page->param("submitted");
      if($submit == 1) {  #è stato fatto submit, devo controllare i dati ed eventualmente inserire
        # TODO controlli, eventuali errori altrimenti inserimento
      }
      else { #primo accesso, devo mostrare la form
        my @padiglioni = ();
        my $i = 0;
        foreach ($resultspad->get_nodelist) {
          $padiglioni[$i]{PADIGLIONE} = $_->findvalue('nome');
          $padiglioni[$i]{SELECTED} = 0;
        }
        
        #compilazione template
        my $template = new HTML::Template(scalarref => \$temp->output(), die_on_bad_params => 0);
        $template->param(PAGE => "Eventi");
        $template->param(KEYWORD => "eventi, EmpireCon, fiera, Impero, Star Wars, Convention");
        $template->param(ADMIN=>$admin);
        $template->param(MOD=>1);
        $template->param(PADIGLIONI=> \@padiglioni);
        $template->param(STRERR=>$strerr);

        HTML::Template->config(utf8=>1);
        print "Content-Type: text/html\n\n", $template->output;
      }
    }
    elsif ($action eq "Modifica") { #modifica di un commento
      # TODO
    }
  }
  else { #c'è un tentativo di modifica da parte di un utente non admin
    #errore TODO
  }
}
else {  #visualizzazione o elimina
  # RECUPERO TUTTI GLI EVENTI
  my $results = $root->findnodes('//evento');
  
  if ($mod=1 and $action eq "Elimina") { #elimina evento
    my $id = $page->param("id");
    my $node = $root->findnodes("//evento[id='$id']")->get_node(1) or do {
      $errori = 1;
      $strerr .= "L'evento selezionato non esiste.<br />";
    };
    
    $node->parentNode->removeChild($node) or die("Fallimento di unbind");
    $doc->toFile($filedati) or die("Fallimento in scrittura");
    print $page->header(-location => "eventi.cgi");
    #trattare errori TODO
  } #fine eliminazione
  
  my @eventi = ();
  my %row;
  my $i = 0;
  foreach ($results->get_nodelist) {
    $row{ADMIN} = $admin;
    $row{ID} = $_->findvalue('id');
    $row{NOME} = $_->findvalue('nome');
    $row{DESCRIZIONE} = $_->findvalue('descrizione');
    $row{PADIGLIONE} = $_->findvalue('padiglione');
    $row{DATA} = italianize_date($_->findvalue('data'));
    $row{INIZIO} = rem_seconds($_->findvalue('inizio'));
    $row{FINE} = rem_seconds($_->findvalue('fine'));
    #creo dataora per il sorting
    my $dt = $_->findvalue('data');
    my $th = $_->findvalue('inizio');
    $th =~ /(\d{2}):(\d{2}):(\d{2})/;
    $dt .= "T" . $0 . $1 . $2;
    $row{DATETIME} = $dt;
    foreach my $key (keys %row) {
      $eventi[$i]{$key}=$row{$key};
    }
    $i += 1;
  }

  #leggo il tipo di ordinamento
  #  0/null -> AZ
  #  1 -> datetime
  #  2 -> padiglioni
  $ord = $page->param('sort');
  my @sortedevents = ();
  if($ord == 2) { #padiglioni
    @sortedevents = sort { $a->{PADIGLIONE} <=> $b->{PADIGLIONE} } @eventi;
  }
  elsif ($ord == 1) { #datetime
    @sortedevents = sort { $a->{DATETIME} <=> $b->{DATETIME} } @eventi;
  }
  else { #AZ
    @sortedevents = sort { $a->{NOME} <=> $b->{NOME} } @eventi;
  }
    

  #compilazione template
  my $template = new HTML::Template(scalarref => \$temp->output(), die_on_bad_params => 0);
  $template->param(PAGE => "Eventi");
  $template->param(KEYWORD => "eventi, EmpireCon, fiera, Impero, Star Wars, Convention");
  $template->param(ADMIN=>$admin);
  $template->param(EVENTI=> \@sortedevents);

  HTML::Template->config(utf8=>1);
  print "Content-Type: text/html\n\n", $template->output;
} #fine visualizzazione



sub italianize_date {
  my $tdata = @_[0];
  $tdata =~ /(\d{4})-(\d{2})-(\d{2})/;
  return $3 . "/" . $2 . "/" . $1;
}

sub rem_seconds {
  my $th = @_[0];
  $th =~ /(\d{2}):(\d{2})/;
  return $1 . ":" . $2;
}
