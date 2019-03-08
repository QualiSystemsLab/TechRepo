*** Variables ***
${CiscoRouter}               Juniper EX 4200
${JuniperRouter}             Cisco Catalyst 3560

*** Test Cases ***
BPG Neightbors are discovered correctly
    [Tags]  bgp
    Validate Router BGP Neighbors   ${CiscoRouter}      1
    Validate Router BGP Neighbors   ${JuniperRouter}    1

OSPF Neightbors are discovered correctly
    [Tags]  ospf
    Validate Router OSPF Neighbors   ${CiscoRouter}      1
    Validate Router OSPF Neighbors   ${JuniperRouter}    1

*** Keywords ***
Validate Router BGP Neighbors
    [Arguments]    ${router}    ${neighbors}
    Log To Console  ${router}

Validate Router OSPF Neighbors
    [Arguments]    ${router}    ${neighbors}
    Log To Console  ${router}
    