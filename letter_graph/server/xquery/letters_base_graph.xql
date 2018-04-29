xquery version "3.1" encoding "UTF-8";
declare namespace tei="http://www.tei-c.org/ns/1.0";

let $listPersons := doc("/db/apps/Letters1916/data/listPerson.xml")//tei:listPerson
let $letters := collection("/db/apps/Letters1916/data/")//tei:TEI[.//tei:teiHeader/@xml:id != 'L1916PersonsList']

let $lettersPersonsIds := 
	distinct-values(collection("/db/apps/Letters1916/data/")//tei:TEI//tei:correspAction/tei:persName/substring(@ref, 2))


return
    <graphml xmlns="http://graphml.graphdrawing.org/xmlns"  
    		 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    		 xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">


        <key id="label" for="node" attr.name="label" attr.type="string">
            <default>NOLABEL</default>
        </key>
        <key id="type" for="node" attr.name="type" attr.type="string"/>
        <key id="title" for="node" attr.name="title" attr.type="string"/>
        <key id="node_color" for="node" attr.name="color" attr.type="string"/>
        <key id="letter_id" for="node" attr.name="letter_id" attr.type="string"/>
        <key id="lighten_color" for="node" attr.name="lighten_color" attr.type="string"/>
        <key id="edge_label" for="edge" attr.name="edge_label" attr.type="string"/>
        <key id="edge_type" for="edge" attr.name="edge_type" attr.type="string"/>
        
        <graph id="G" edgedefault="directed">
        	{

        		for $personId in $lettersPersonsIds
        			let $person := $listPersons//tei:person[@xml:id=$personId]
	        		return
	        			<node id="{$personId}">
		        			<data key="label">{$person/tei:persName/string()}</data>
	                        <data key="type">Person</data>
	        				
	        			</node>

        	}

        	{
        		for $letter in $letters
        			return
        			    <node id="{$letter//tei:teiHeader/substring(@xml:id, 7)}">
        			    	<data key="title">{$letter//tei:titleStmt//tei:title/string()}</data>
        					<data key="type">Letter</data>
        			    </node>
        	}

        	
        	{		
        		for $letter in $letters
        		    let $senders := $letter//tei:correspDesc[@xml:id="corresp1"]/tei:correspAction[@type='sent']//tei:persName
        		    let $letterId := $letter//tei:teiHeader/substring(@xml:id, 7)

        			return 
        			    for $sender in $senders
        			    	let $senderRef := $sender/substring(@ref, 2)
            			    
            			    return
            			    	<edge source="{$senderRef}" target="{$letterId}">
                                    <data key="edge_type">SenderToLetter</data>
                                </edge>
                         
        	
        	}
        	{
        	    for $letter in $letters
        		    let $recipients := $letter//tei:correspDesc[@xml:id="corresp1"]/tei:correspAction[@type='received']//tei:persName
        		    let $letterId := $letter//tei:teiHeader/substring(@xml:id, 7)

        		    return
        		        for $recipient in $recipients
        		        	let $recipientRef := $recipient/substring(@ref, 2)

        		            return 
        	                	<edge source="{$letterId}" target="{$recipientRef}">
                                    <data key="edge_type">LetterToRecipient</data>
                                </edge>
        	        
        	}

        </graph>
    </graphml>