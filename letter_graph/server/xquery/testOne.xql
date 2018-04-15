xquery version "3.1" encoding "UTF-8";

let $name := request:get-parameter('name', 'default value')
let $thing := request:get-parameter('other', 'default value')
return
  <results timestamp="{current-dateTime()}">
     <message>{$name} loves dancing the tango with {$thing}</message>
  </results>
