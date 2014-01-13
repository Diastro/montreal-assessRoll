montreal-assessRoll
===================

Automated Montreal assessment roll querying

*** More to come ***

##Execution
1) Download the source and install the required third party library
~~~ sh
$ git clone https://github.com/Diastro/montreal-assessRoll.git
$ easy_install beautifulsoup4
$ easy_install lxml
~~~

2) Launch the python file
~~~ sh
$ pyhton assessment_roll.py
~~~

3) Answer the required field during the execution

####Third party library
- [BeautifulSoup4](http://www.crummy.com/software/BeautifulSoup/)
- [lxml](http://lxml.de/)

## Output example
~~~ sh
123 121th Street, BROSNAN PIERRE, 800 039 $
345 Papineau Blvd, GREEN MATHEW, 639 928 $
8720 Henri Bourassa, PHILIPS ISABELLE, 392 000 $
~~~

