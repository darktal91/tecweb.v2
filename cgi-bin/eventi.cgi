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

# RECUPERO I PADIGLIONI DA XML
my $filepad = "../data/padiglioni/padiglioni.xml";
my $parserpad = XML::LibXML -> new(); #creo il parser
#apertura file
my $docpad = $parserpad->parse_file($filepad) || die("Operazione di parsificazione padiglioni fallita");
#leggo la radice
my $rootpad = $docpad->getDocumentElement || die("Accesso alla radice padiglioni fallita");

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
my $template = new HTML::Template(scalarref => \$temp->output(), die_on_bad_params => 0);
$template->param(PAGE => "Eventi");
$template->param(KEYWORD => "eventi, EmpireCon, fiera, Impero, Empire, Star Wars, Convention");
$template->param(ADMIN=>$admin);

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
    my $resultspad = $rootpad->findnodes('//padiglione');
    
    if ($action eq "" or $action eq "Nuovo") {
      #sono in azione di nuovo evento
      my $submit = $page->param("submitted");
      if($submit == 1) {  #è stato fatto submit, devo controllare i dati ed eventualmente inserire
        my $nnome = $page->param("nome");
        my $ndesc = $page->param("descrizione");
        my $npad = $page->param("padiglione");
        my $ndata = $page->param("data");
        my $ninizio = $page->param("inizio");
        my $nfine = $page->param("fine");
        
        # CONTROLLI SUI DATI
        chk_data($ndata);
        chk_ora($ninizio, "inizio");
        chk_ora($nfine, "fine");
        if ($nnome eq "") {
	  $errori = 1;
	  $strerr .= "Il nome dell'evento non può essere vuoto. <br /> ";
        }
        if ($ndesc eq "") {
	  $errori = 1;
	  $strerr .= "Il campo descrizione non può essere vuoto. <br /> ";
        }
        #controllo padiglioni
        if ($rootpad->exists("//padiglione[nome='$npad']") == 0) {
	  #il padiglione inserito non esiste
	  $errori = 1;
	  $strerr .= "Il padiglione inserito non esiste.";
        }
        # controllo che l'id sia univoco
        $nid = encode_base64($nnome);
        chomp($nid);
        if ($root->exists("//evento[id='$nid']") != 0) {
	  $errori = 1;
	  $strerr .= "Il nome dell'evento inserito è già esistente. <br />";
        }
        #FINE CONTROLLI
	
	#passaggio parametri a template
        $template->param(MOD=>1);
	
	#se errore=1 -> ci sono stati errori
	#se errore=0 -> non ci sono stati errori
	if ($errori == 1) {  #ci sono stati errori.
	  #preparo array padiglioni
	  my @padiglioni = ();
	  my $i = 0;
	  foreach ($resultspad->get_nodelist) {
	    $padiglioni[$i]{PADIGLIONE} = $_->findvalue('nome');
	    if($npad eq $padiglioni[$i]{PADIGLIONE}) {
	      $padiglioni[$i]{SELECTED} = 1;
	    }
	    else {
	      $padiglioni[$i]{SELECTED} = 0;
	    }
	    $i += 1;
	  }
	  
	  $template->param(OK=>0);
	  $template->param(PADIGLIONI=> \@padiglioni);
	  $template->param(NOME=>$nnome);
	  $template->param(DESCRIZIONE=>$ndesc);
	  $template->param(DATA=>$ndata);
	  $template->param(INIZIO=>$ninizio);
	  $template->param(FINE=>$nfine);
	}
	else { # NON CI SONO STATI ERRORI, INSERISCO
	  #preparo orari in formato iso corretto
	  $norminizio = $ninizio . ":00";
	  $normfine = $nfine . ":00";

	  # creo i nuovi nodi
	  my $new_evento = $doc->createElement("evento");
	  my $new_id = $doc->createElement("id");
	  my $new_nome = $doc->createElement("nome");
	  my $new_descrizione = $doc->createElement("descrizione");
	  my $new_padiglione = $doc->createElement("padiglione");
	  my $new_data = $doc->createElement("data");
	  my $new_inizio = $doc->createElement("inizio");
	  my $new_fine = $doc->createElement("fine");
	  # inserisco i nuovi nodi
	  $new_evento->addChild($new_id);
	  $new_evento->addChild($new_nome);
	  $new_evento->addChild($new_descrizione);
	  $new_evento->addChild($new_padiglione);
	  $new_evento->addChild($new_data);
	  $new_evento->addChild($new_inizio);
	  $new_evento->addChild($new_fine);
	  $root->addChild($new_evento);
	  # inserisco dati nei nodi
	  $new_id->appendText($nid);
	  $new_nome->appendText($nnome);
	  $new_descrizione->appendText($ndesc);
	  $new_padiglione->appendText($npad);
	  $new_data->appendText($ndata);
	  $new_inizio->appendText($norminizio);
	  $new_fine->appendText($normfine);
	  
	  # stampo le modifiche su xml
	  $doc->toFile($filedati);

	  #passo parametri al template
	  $template->param(OK=>1);
	}
      }
      else { #primo accesso, devo mostrare la form
        my @padiglioni = ();
        my $i = 0;
        foreach ($resultspad->get_nodelist) {
          $padiglioni[$i]{PADIGLIONE} = $_->findvalue('nome');
          $padiglioni[$i]{SELECTED} = 0;
          $i += 1;
        }
        
        #passaggio parametri a template
        $template->param(MOD=>1);
        $template->param(PADIGLIONI=> \@padiglioni);

      }
    }
    elsif ($action eq "Modifica") { #modifica di un evento
      $id = $page->param("id");
      chomp($id);

      my $submit = 0; 
      $submit = $page->param("submitted");
      if ($submit == 0) { #primo accesso
	my %dati; #hash per contenere i dati
	#estraggo i dati da XML
	my $results = $root->findnodes("//evento[id='$id']") or die("$id");
	foreach my $context ($results->get_nodelist) {
	  $dati{"nome"} = encode('UTF-8', $context->findvalue("nome"), Encode::FB_CROAK);
	  $dati{"descrizione"} = encode('UTF-8', $context->findvalue("descrizione"), Encode::FB_CROAK);
	  $dati{"padiglione"} = $context->findvalue("padiglione");
	  $dati{"data"} = $context->findvalue("data");
	  $dati{"inizio"} = rem_seconds($context->findvalue("inizio"));
	  $dati{"fine"} = rem_seconds($context->findvalue("fine"));
	}
	
	#preparo array padiglioni
	my @padiglioni = ();
        my $i = 0;
        foreach ($resultspad->get_nodelist) {
          $padiglioni[$i]{PADIGLIONE} = $_->findvalue('nome');
          if ($padiglioni[$i]{PADIGLIONE} eq $dati{"padiglione"}) {
	    $padiglioni[$i]{SELECTED} = 1;
	  }
	  else {
	    $padiglioni[$i]{SELECTED} = 0;
	  }
          $i += 1;
        }
	
	#passaggio parametri a template
        $template->param(MOD=>1);
        $template->param(PADIGLIONI=> \@padiglioni);
        $template->param(MODIFICA=>1);
        $template->param(ID=>$id);
        $template->param(NOME=>$dati{"nome"});
        $template->param(DESCRIZIONE=>$dati{"descrizione"});
        $template->param(DATA=>$dati{"data"});
        $template->param(INIZIO=>$dati{"inizio"});
        $template->param(FINE=>$dati{"fine"});

      }
      else { # modifica avvenuta
	my %cambiati; #hash per contenere i valori modificati
	#recupero i valori modificati
	$cambiati{"descrizione"} = $page->param("descrizione");
	$cambiati{"padiglione"} = $page->param("padiglione");
	$cambiati{"data"} = $page->param("data");
	$cambiati{"inizio"} = $page->param("inizio");
	$cambiati{"fine"} = $page->param("fine");
	
	# CONTROLLO SUI DATI
	chk_data($cambiati{"data"});
	chk_ora($cambiati{"inizio"}, "inizio");
	chk_ora($cambiati{"fine"}, "fine");
	if ($cambiati{"descrizione"} eq "") {
	  $errori = 1;
	  $strerr .= "Il campo descrizione non può essere vuoto. <br /> ";
	}
	#controllo padiglioni
        if ($rootpad->exists("//padiglione[nome='$cambiati{padiglione}']") == 0) {
	  #il padiglione inserito non esiste
	  $errori = 1;
	  $strerr .= "Il padiglione inserito non esiste.";
        }
        #fine controlli
        
        if ($errori == 0) { #TUTTO OK, PROCEDO ALLA MODIFICA
	  #descrizione
	  my $moddesc = $doc->findnodes("//evento[id='$id']/descrizione/text()")->get_node(1) or die("Fallimento nel recupero del nodo per la modifica");
	  $moddesc->setData($cambiati{"descrizione"});
	  
	  #padiglione
	  my $modpad = $doc->findnodes("//evento[id='$id']/padiglione/text()")->get_node(1) or die("Fallimento nel recupero del nodo per la modifica");
	  $modpad->setData($cambiati{"padiglione"});
	  
	  #data
	  my $moddata = $doc->findnodes("//evento[id='$id']/data/text()")->get_node(1) or die("Fallimento nel recupero del nodo per la modifica");
	  $moddata->setData($cambiati{"data"});
	  
	  #inizio
	  my $norminizio = $cambiati{"inizio"} . ":00";
	  my $modinizio = $doc->findnodes("//evento[id='$id']/inizio/text()")->get_node(1) or die("Fallimento nel recupero del nodo per la modifica");
	  $modinizio->setData($norminizio);
	  
	  #fine
	  my $normfine = $cambiati{"fine"} . ":00";
	  my $modfine = $doc->findnodes("//evento[id='$id']/fine/text()")->get_node(1) or die("Fallimento nel recupero del nodo per la modifica");
	  $modfine->setData($normfine);
	  
	  $doc->toFile($filedati) or die("Fallimento in scrittura");
	  
	  #passaggio parametri a template
	  $template->param(MOD=>1);
	  $template->param(MODIFICA=>1);
	  $template->param(OK=>1);

        }
        else { # ci sono stati degli errori, rimando i dati modificati al template insieme agli errori
	  # preparo array padiglioni
	  my @padiglioni = ();
	  my $i = 0;
	  foreach ($resultspad->get_nodelist) {
	    $padiglioni[$i]{PADIGLIONE} = $_->findvalue('nome');
	    if ($padiglioni[$i]{PADIGLIONE} eq $cambiati{"padiglione"}) {
	      $padiglioni[$i]{SELECTED} = 1;
	    }
	    else {
	      $padiglioni[$i]{SELECTED} = 0;
	    }
	    $i += 1;
	  }
	  
	  #passaggio parametri a template
	  $template->param(MOD=>1);
	  $template->param(PADIGLIONI=> \@padiglioni);
	  $template->param(MODIFICA=>1);
	  $template->param(ID=>$id);
	  $template->param(NOME=>$cambiati{"nome"});
	  $template->param(DESCRIZIONE=>$cambiati{"descrizione"});
	  $template->param(DATA=>$cambiati{"data"});
	  $template->param(INIZIO=>$cambiati{"inizio"});
	  $template->param(FINE=>$cambiati{"fine"});
        }
      }
    }
  }
  else { #c'è un tentativo di modifica da parte di un utente non admin
    $strerr .= "Non si posseggono i permessi necessari per eseguire azioni di modifica. <br />";
  }
}
else {  #visualizzazione o elimina
  # RECUPERO TUTTI GLI EVENTI
  my $results = $root->findnodes('//evento');
  
  if ($mod=1 and $action eq "Elimina") { #elimina evento
    my $id = $page->param("id");
    chomp($id);
    #eliminazione da eventi
    my $node = $root->findnodes("//evento[id='$id']")->get_node(1) or do {
      $errori = 1;
      $strerr .= "L'evento selezionato non esiste.<br />";
    };
    $node->parentNode->removeChild($node) or die("Fallimento di unbind evento");
    $doc->toFile($filedati) or die("Fallimento in scrittura eventi");
    
    print $page->header(-location => "eventi.cgi");
  } #fine eliminazione
  
  my @eventi = ();
  my %row;
  my $i = 0;
  foreach ($results->get_nodelist) {
    $row{ADMIN} = $admin;
    $row{ID} = $_->findvalue('id');
    $row{NOME} = encode('UTF-8', $_->findvalue('nome'), Encode::FB_CROAK);
    $row{DESCRIZIONE} = encode('UTF-8', $_->findvalue('descrizione'), Encode::FB_CROAK);
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
  #  0/null -> padiglioni
  #  1 -> datetime
  #  2 -> AZ
  $ord = $page->param('sort');
  my @sortedevents = ();
  if($ord == 2) { #AZ
    @sortedevents = sort { lc($a->{NOME}) cmp lc($b->{NOME}) } @eventi;
    $template->param(ORDAZ=>1);
  }
  elsif ($ord == 1) { #datetime
    @sortedevents = sort { lc($a->{DATETIME}) cmp lc($b->{DATETIME}) } @eventi;
    $template->param(ORDDT=>1);
  }
  else { #padiglioni
    @sortedevents = sort sortdatapadiglione @eventi;
    $template->param(ORDPAD=>1);
    my @A = @B = @C = @D = @E = @F = @G = @H = ();
    my $a = $b = $c = $d = $e = $f = $g = $h = 0;
    
    for (my $j=0; $j<$i; $j++) {
      if ($sortedevents[$j]{PADIGLIONE} eq "A") { 
	foreach my $keys (keys %{$sortedevents[$j]}) {
	  $A[$a]{$keys} = $sortedevents[$j]{$keys};
	}
	$a +=1;
      }
      elsif ($sortedevents[$j]{PADIGLIONE} eq "B") { 
	foreach my $keys (keys %{$sortedevents[$j]}) {
	  $B[$b]{$keys} = $sortedevents[$j]{$keys};
	}
	$b +=1;
      }
      elsif ($sortedevents[$j]{PADIGLIONE} eq "C") { 
	foreach my $keys (keys %{$sortedevents[$j]}) {
	  $C[$c]{$keys} = $sortedevents[$j]{$keys};
	}
	$c +=1;
      }
      elsif ($sortedevents[$j]{PADIGLIONE} eq "D") { 
	foreach my $keys (keys %{$sortedevents[$j]}) {
	  $D[$d]{$keys} = $sortedevents[$j]{$keys};
	}
	$d +=1;
      }
      elsif ($sortedevents[$j]{PADIGLIONE} eq "E") { 
	foreach my $keys (keys %{$sortedevents[$j]}) {
	  $E[$e]{$keys} = $sortedevents[$j]{$keys};
	}
	$e +=1;
      }
      elsif ($sortedevents[$j]{PADIGLIONE} eq "F") { 
	foreach my $keys (keys %{$sortedevents[$j]}) {
	  $F[$f]{$keys} = $sortedevents[$j]{$keys};
	}
	$f +=1;
      }
     elsif ($sortedevents[$j]{PADIGLIONE} eq "G") { 
	foreach my $keys (keys %{$sortedevents[$j]}) {
	  $G[$g]{$keys} = $sortedevents[$j]{$keys};
	}
	$g +=1;
      }
      elsif ($sortedevents[$j]{PADIGLIONE} eq "H") { 
	foreach my $keys (keys %{$sortedevents[$j]}) {
	  $H[$h]{$keys} = $sortedevents[$j]{$keys};
	}
	$h +=1;
      }
    }
    
    $template->param(A=> \@A);
    $template->param(B=> \@B);
    $template->param(C=> \@C);
    $template->param(D=> \@D);
    $template->param(E=> \@E);
    $template->param(F=> \@F);
    $template->param(G=> \@G);
    $template->param(H=> \@H);
  }
    

  #passaggio parametri a template
  $template->param(EVENTI=> \@sortedevents);

  
} #fine visualizzazione

$template->param(ERRORI=>$errori);
$template->param(STRERR=>$strerr);
HTML::Template->config(utf8=>1);
print "Content-Type: text/html\n\n", $template->output;

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


# funzione di controllo correttezza data
sub chk_data {
  my $d = $_[0];
  
  if($d eq "") {
    #la data è vuota
    $errori = 1;
    $strerr .= "Il campo data non può essere vuoto. <br />";
  }
  elsif ($d !~ /^((20)\d{2})\-(0[1-9]|1[012])-(0[1-9]|[12]\d|3[01])$/) { 
    #la data non ha un formato valido
    $errori = 1;
    $strerr .= "La data inserita non ha un formato valido. Usare il formato aaaa-mm-gg.<br />";
  }
  else {  #la data ha un formato valido. 
    #  controllo esistenza giorno-mese
    if ($4 == 31 and ($3 == 4 or $3 == 6 or $3 == 9 or $3 == 11)) {
	#giorno 31 in un mese da 30 giorni. errore.
	$errori = 1;
	$strerr .= "Data inserita non valida. <br />";
    }
    elsif ($3 == 2) { #controllo se il mese è febbraio
      #controllo se il giorno è 30 o 31
      if ($4 >= 30) {
	# febbraio non ha i giorni 30 e 31, errore.
	$errori = 1;
	$strerr .= "Data inserita non valida. <br />";
      }
      #controllo se il giorno è 29 ma l'anno non è bisestile
      elsif ($4 == 29 and not (($1 % 400) == 0 or (($1 % 100) != 0 and ($1 % 4) == 0))) {
	#giorno 29 febbraio in un anno NON bisestile, errore.
	$errori = 1;
	$strerr .= "Data inserita non valida. <br />";
      }
    }
  }
}

#funzione di controllo correttezza ora
sub chk_ora {
  my $h = $_[0];
  my $discr = $_[1]; #discriminante inizio/fine
  
  if($h eq "") {
    #l'ora non può essere vuota
    $errori = 1;
    $strerr .= "L'ora di $discr non può essere vuota. <br />";
  }
  elsif($h !~ /^(([01]\d|2[0-4]):([0-5]\d))$/) {
    # l'ora non ha un formato corretto
    $errori = 1;
    $strerr .= "L'ora di $discr ha un formato non corretto. Usare il formato hh:mm. <br />";
  }
  else {
    # l'ora ha un formato corretto, controllo validità
    if ($1 == 24 and $2 ne "00") {
      #24:xx con xx diverso da zero non viene accettato
      $errori = 1;
      $strerr .= "L'ora di $discr non è valida. Deve essere nell'intervallo 00:00 - 24:00. <br />";
    }
  }
}

sub sortdatapadiglione {
 return ($a->{DATETIME} cmp $b->{DATETIME}) if ($a->{PADIGLIONE} eq $b->{PADIGLIONE});
 return $a->{PADIGLIONE} cmp $b->{PADIGLIONE};
}