xquery version "3.1" encoding "UTF-8";

let $name := request:get-parameter('name', 'default value')
let $thing := request:get-parameter('other', 'default value')

return
  <GraphML>
     <message>{$name} is connected in a graph to {$thing}</message>
  </GraphML>
