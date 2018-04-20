xquery version "3.1" encoding "UTF-8";
declare namespace tei="http://www.tei-c.org/ns/1.0";

let $persons := doc("/db/apps/Letters1916/data/listPerson.xml")//tei:listPerson
let $letters := collection("/db/apps/Letters1916/data/")//tei:TEI

for $corresp in $letters//tei:correspDesc//tei:persName/@ref
	return $persons/tei:person[@xml:id=concat('#', $corresp)]