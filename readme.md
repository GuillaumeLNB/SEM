# SEM v3.0.0
[SEM (Segmenteur-Étiqueteur Markovien)](http://www.lattice.cnrs.fr/sites/itellier/SEM.html) is a free NLP tool relying on Machine Learning technologies, especially CRFs. SEM provides powerful and configurable preprocessing and postprocessing. [SEM also has an online version](http://apps.lattice.cnrs.fr/sem/index).

## Main SEM features
1. A GUI for easier use (requires TkInter)
   1. on Linux: double-clic on sem_gui.sh
   2. on Windows: double-clic on sem_gui.bat
   3. from temrinal: run ```python -m sem gui```
2. segmentation
   1. segmentation for: French, English
   2. easy creation and integration of new tokenisers
3. feature generation
   1. XML file to write features without coding them
   2. single-token and multi-token dictionary features
   3. Regular expression features
   4. sequenced features
   5. train/label mode
   6. display option for features that are useful for generation, but not needed in output
4. exporting output
   1. supported export formats: CoNLL, text, HTML (from plain text), two XML-TEI (one specific to NP-chunks and another one for the rest)
   2. easy creation and integration of new exporters
5. extension of existing features
   1. automatic integration of new segmenters and exporters
   2. semi automatic integration of new feature functions
   3. easy creation of new CSS formats for HTML exports

## First steps with SEM
1. install SEM
   1. run ```python setup.py install --user``` to install SEM. It will compile Wapiti and create necessary directories. Currently, SEM datas are located in ```~/sem_data```
   2. on Windows, Wapiti compilation may fail. Check you use the right gcc (see in make.bat)
   3. note: on Windows, either install [POSIX threads for Windows](https://sourceforge.net/p/pthreads4w/wiki/Home/) or disable them as explained in ext/src/wapiti.h
2. run tests
   1. run ```python -m sem --test``` in a terminal
3. run SEM
   1. run GUI (see "main features" above) and annotate "non-regression/fr/in/segmentation.txt"
   2. OR: run ```python -m sem tagger resources/master/fr/NER.xml ./non-regression/fr/in/segmentation.txt -o sem_output```

## External resources used by SEM
1. [French Treebank](http://www.llf.cnrs.fr/fr/Gens/Abeille/French-Treebank-fr.php) by [Abeillé et al. (2003)](http://link.springer.com/chapter/10.1007%2F978-94-010-0201-1_10): corpus used for POS and chunking.
2. NER annotated French Treebank by [Sagot et al. (2012)](https://halshs.archives-ouvertes.fr/file/index/docid/703108/filename/taln12ftbne.pdf): corpus used for NER.
3. [Lexique des Formes Fléchies du Français (LeFFF)](http://alpage.inria.fr/~sagot/lefff.html) by [Clément et al. (2004)](http://www.labri.fr/perso/clement/lefff/public/lrec04ClementLangSagot-1.0.pdf): french lexicon of inflected forms with various informations, such as their POS tag and lemmatization.
4. [Wapiti](http://wapiti.limsi.fr) by [Lavergne et al. (2010)](http://www.aclweb.org/anthology/P10-1052): linear-chain CRF library.
5. Windows only: [MinGW64](https://sourceforge.net/projects/mingw-w64/?source=navbar): used to compile Wapiti on Windows.
6. Windows only: [POSIX threads for Windows](https://sourceforge.net/p/pthreads4w/wiki/Home/): if you want to multithread Wapiti on Windows.
7. GUI-specific: [TkInter](https://wiki.python.org/moin/TkInter): if you want to launch SEM's GUI.

## Latest changes (2.5.4 > 3.0.0)
1. improved SEM architecture.
2. SEM can now be installed.
   1. run ```python setup.py install --user```
   2. will compile Wapiti
   3. will create a sem_data folder in current user
3. imrpoved GUI
   1. SEM can now train a Wapiti model using annotated files.
4. another GUI created for annotating documents.
5. updated manual
6. new module: __annotate__. allows to call python taggers
   1. python implementation of Wapiti labeling
   2. lexica-based tagger

## Planned changes (no priority)
1. Add a tutorial.
2. redo triggered features and sequence features.
3. add lemmatiser.
4. migration to python3 ? (already made for revision 39 by lerela).
5. translate manual in English.
6. have more unit tests
7. handle HTML input files for tagger module
   1. create specific tokeniser
   2. need to handles cases such as words cut by a HTML tag
8. improve segmentation
   1. handle URLs starting with country indicator (ex: "en.wikipedia.org")
   2. handle URLs starting with subdomain (ex: "blog.[...]")

## SEM references (with task[s] of interest)
1. [TELLIER, Isabelle, DUCHIER, Denys, ESHKOL, Iris, et al. Apprentissage automatique d'un chunker pour le français. In : TALN2012. 2012. p. 431–438.](https://hal.archives-ouvertes.fr/hal-01174591/document)
   1. Chunking
2. [TELLIER, Isabelle, DUPONT, Yoann, et COURMET, Arnaud. Un segmenteur-étiqueteur et un chunker pour le français. JEP-TALN-RECITAL 2012](http://anthology.aclweb.org/F/F12/F12-5.pdf#page=27)
   1. Part-Of-Speech Tagging
   2. chunking
3. [DUPONT, Yoann et TELLIER, Isabelle. Un reconnaisseur d’entités nommées du Français. session démonstration de TALN, 2014, p. 40.](http://www.aclweb.org/anthology/F/F14/F14-3.pdf#page=42)
   1. Named Entity Recognition
