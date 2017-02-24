# README #

Richiede Python 3.5.1.

Installare le dipendenze elencate nel file `requirements.txt`.

### Per il supporto al costrutto OPTION INFERENCE di Virtuoso ###

Dopo aver installato le dipendenze, sostituire il file `parser.py` di RDFLib con il file: `sparql_license_checker/utils/parser.py`.

Per trovare il path del file da sostituire eseguire i seguenti comandi python:
```
from rdflib.plugins import sparql
print(sparql.parser.__file__)
```
### Configurazione ###

Il file `sparql_license_checker/python_sparql_licence/config.cfg`
contiene le configurazioni per il server python e mysql.

Il file `sparql_license_checker/utils/db_changes.sql` contiene delle istruzioni sql da eseguire sul database SiiMobility per un corretto funzionamento del tool.