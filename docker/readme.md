# Docker

## Premessa
Ho creato un makefile al volo, non è perfetto ma fa quello che deve fare.
I passaggi per usare docker sono:
* procurarsi un'immagine, creandosela o scaricandone una già buildata dal repo delle immagini su dockerhub
* avviare il container specificando eventuali volumi per la persistenza dei dati

## makefile
I comandi disponibili sono:

1. ``` make pull ```

  Scarica l'immagine che ho creato io dal mio dockerhub
  
2. ``` make run ```

  Avvia il container e lo nomina tecweb-server, includendo le cartelle cgi-bin, pucblic_html e data (presenti nel repo, lo fa tramite path relativo) e forwards la porta 9999 dell'host alla porta 80 del container
  
3. ``` make stop ```

  Ferma il container, senza però rimuoverlo. Per farlo ripartire bisogna usare il comando docker start tecweb-server, non presente nel makefile. Consiglio quindi di usare sempre il comando seguente
  
4. ``` make clean ```

  Arresta il container tecweb-server e lo rimuove, eliminando tutto ciò che non è persistente (cioè tutto tranne le tre cartelle del repo). Consiglio di usare sempre questo comando per fermare il container, permette di ripartire sempre con un container nuovo e pulito facendo make run.
  
5. ``` make shell ```

  Utilizzabile solo ed esclusivamente quando il container è in esecuzione, permette di avviare un accesso alla shell del container (figurativamente è come collegarsi in ssh ad un server remoto). Tutti i comandi eseguiti di seguito saranno eseguiti dalla shell del container, e come per una sessione ssh di interrompe col comando exit.
  
6. gli altri due comandi non dovrebbero servirvi, li uso io per gestire le immagini e le modifiche alle immagini in locale, li ho lasciati solo per completezza e nel caso in cui facessi qualche pasticcio con l'immagine.

## Accedere al progetto dal browser
Come specificato nella lista dei comandi del makefile, all'avvio del container viene specificato il forwarding della porta 9999 dell'host sulla porta 80 del container, quindi per visualizzare il progetto basta usare l'url [localhost:9999/tecweb](localhost:9999/tecweb). Ovviamente funziona solo quando il container è in esecuzione ;)

## Esempio di utilizzo
``` make pull ``` (solo la prima volta, scarica l'immagine dal repo)

``` make run ``` (avvia il container)

Una volta finito, ``` make clean ``` per fermare il container e rimuoverlo.

In caso di problemi, ``` make shell ``` per accedere alla shell del container. Una volta terminato, ``` exit ``` per terminare l'istanza della shell.