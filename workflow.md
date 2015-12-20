## Workflow

### Premessa
Questo è un tentativo di adottare un workflow tramite branch discusso [qui](http://nvie.com/posts/a-successful-git-branching-model/).
Data la mancanza di esperienza, questa mini guida sarà (quasi) sicuramente soggetta a cambiamenti e correzioni

### Branch
Il repo sarà basato su due branch principali, il branch **master** e il branch **develop**.
Il branch *master* dovrà trovarsi sempre in uno stato stabile e privo di errori, tutti i merge eseguiti su master dovranno essere prima testati e controllati a fondo per evitare l'introduzione di errori.
Il branch *develop*, invece, è il branch di lavoro, e contiene sempre le ultime modifiche apportate al codice. Per questo motivo può essere soggetto ad errori.

#### Comandi base per il branching con git
###### Visualizzare i branch esistenti ed il branch in cui ci si trova al momento:
``` 
git branch 
```

###### Passare ad un altro branch:
``` 
git checkout _nomebranch_ 
```

###### Creare un nuovo branch:


```
git checkout -b _nomebranch_
```
Questo comando crea il nuovo branch e fa anche il checkout in esso. Se si vuole solamente creare il nuovo branch senza però fare il checkout:
```
git branch _nomebranch_
```

###### Eseguire un merge:

Per eseguire un merge è necessario spostarsi (_checkout_) nel branch in cui si vuole effettuare il merge, e da li eseguire il merge del branch che si vuole mergiare. In comandi:
```
git checkout _branch_in_cui_effettuare_il_merge_
git merge --no-ff _branch_che_si_vuole_mergiare_
```
Ad esempio, supponiamo di avere due branch, chiamati _A_ e _B_. _B_ è il branch che contiene le modifiche e che si vuole andare a mergiare nel branch principale, mentre _A_ è il branch principale in cui si andare a mergiare il branch _B_. Quindi:
```
git checkout A
git merge --no-ff B
```
**Attenzione ai conflitti!**

###### Eliminare un branch:

Quando un branch termina la sua utilità, ad esempio quando l'issue corrispondente è stata risolta, e dopo un eventuale merge, si può voler eliminare un branch. Per fare ciò:
```
git branch -d _nomebranch_
```


#### Struttura dei branch
Come premesso, il workflow in questo progetto sarà un tentativo di adottare il sistema di branching proposto nell'articolo linkato precedentemente.
I branch utilizzati saranno, quindi:
* master
* develop
* issue##
* feature***
* hotfix#
* eventuale branch release-x.y.z

Più in dettaglio:

###### master
Il branch master è il branch principale, e sarà sempre presente per tutta la durata del progetto.
Il master deve sempre trovarsi in uno stato stabile e privo di errori.

###### develop
Il branch _develop_ è il branch di lavoro, quello in cui si trovano sempre le ultime modifiche apportate al progetto. Da questo branch verranno creati tutti gli altri branch (tranne _hotfix#_), e sempre in questo branch quasi tutti gli altri branch saranno mergiati.

###### issue
Un branch issue## viene creato quando si lavora alla soluzione di una issue aperta, ovviamente i cancelletti vanno sostituiti con il numero della issue corrispondente: ad esempio se si lavora alla issue#42, dovrà essere creato il branch _issue42_.
Un branch _issue_ si stacca sempre dal branch _develop_ ed in esso deve essere mergiato.

Esempio: mi assegno l'issue#42 e la risolvo. 
```
git checkout develop
git checkout -b issue42
_...modifico il codice per risolvere l'issue.._
git checkout develop
git merge --no-ff issue42
git branch -d issue42
```

###### feature***
Un branch feature viene creato per sviluppare una nuova feature al progetto. Nel nostro caso molto probabilmente non sarà necessario dato che il progetto si trova già in uno stato relativamente avanzato, e il lavoro da svolgere è principalmente soluzione di problemi.
Come un branch issue, un branch feature si stacca sempre dal branch _develop_ ed in esso deve essere mergiato.

###### hotfix#
Il branch hotfix serve per correggere errori critici presenti sul branch master, ad esempio _Internal server error_ che sono sfuggiti all'ondata di error fixing.
Il branch hotfix viene sempre e comunque associato ad un'issue su github per completezza e tracciabilità.
Il branch hotfix si stacca sempre dal branch _master_ e va mergiato sia nel branch _master_ che nel branch _develop_.

###### eventuali branch release-x.y.z
Eventualmente potremo decidere di utilizzare dei branch release per mergiare nel _master_ il lavoro svolto fino a quel momento in _develop_, per esempio per taggare un determinato momento nella storia dello sviluppo del progetto. In caso ne discuteremo più approfonditamente.

### Note sul workflow
Come intuibile dalla descrizione dei branch, quasi ogni branch viene associato/"richiesto" dall'apertura di una issue su github. Questo passo è molto importante, perchè le issue permettono di mantenere i problemi ed il lavoro tracciati e metodici. Una issue aperta, con conseguente assegnazione, risoluzione e chiusura, permette di poter sempre risalire al _chi, cosa, come, quando e perchè_ di ogni modifica, cioè risalire a:
* natura del problema in dettaglio
* chi se ne occupa
* quando se ne occupa
* come la risolve

La tracciabilità del lavoro è molto importante, ed è uno degli obiettivi che vorrei raggiungere implementando questo modello di lavoro nel progetto.

### Conclusioni
Come da premesse, i membri del gruppo sono relativamente inesperti nell'attuazione di un modello di lavoro rigoroso, strutturato ed organizzato. Essendo questo un progetto didattico, lo scopo principale, dal mio punto di vista, è di sbagliare ed imparare dai propri errori, cercando di apprendere nozioni importanti per lo sviluppo professionale. Di conseguenza, assisteremo ad un elevato numero di errori e pasticci, per esempio con i merge o con la chiusura prematura di branch e issue, ecc. Ciò nonostante, sono sicuro che sarà un'esperienza utile ai fini dell'apprendimento di un metodo di lavoro.

In conclusione, **buona fortuna a tutti, ne avremo bisogno. Ci sarà da divertirsi!**