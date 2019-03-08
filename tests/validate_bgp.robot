*** Variables ***
${CiscoRouter}               Juniper EX 4200
${JuniperRouter}             Cisco Catalyst 3560

*** Test Cases ***
BPG Neightbors are discovered correctly
    Validate Router Neighbors   ${CiscoRouter}      1
    Validate Router Neighbors   ${JuniperRouter}    1

*** Keywords ***
Validate Router Neighbors
    [Arguments]    ${router}    ${neighbors}
    Log To Console  ${router}