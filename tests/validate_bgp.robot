*** Settings ***
Library           OperatingSystem
Library           Collections
Library           String
Library           ../lib/BgpLibrary.py
Library           ../lib/SandboxLibrary.py  ${CloudShellURL}  ${User}  ${Password}  ${Domain}

*** Variables ***
${SandboxId}                 c5cd06a8-9244-45d7-a105-03bff43317f5
${CiscoRouter}               Cisco Catalyst 3560
${CloudShellURL}             
${User}
${Password}     
${Domain}                    Demo Advanced
${JuniperRouter}             Juniper EX 4200

*** Test Cases ***
Juniper BPG Neightbors are discovered correctly
    [Tags]  bgp
    Validate Juniper Router BGP Neighbors   ${JuniperRouter}  1

Cisco BPG Neightbors are discovered correctly
    [Tags]  bgp
    Validate Cisco Router BGP Neighbors   ${CiscoRouter}  1

OSPF Neightbors are discovered correctly
    [Tags]  ospf
    Validate Router OSPF Neighbors   ${CiscoRouter}      1
    Validate Router OSPF Neighbors   ${JuniperRouter}    1

*** Keywords ***
Validate Juniper Router BGP Neighbors
    [Arguments]    ${router}    ${neighbors}
    ${value} =  Get Juniper Router BGP Info  ${router}
    Validate Bgp Groups  ${value}  1

Validate Cisco Router BGP Neighbors
    [Arguments]    ${router}    ${neighbors}
    ${value} =  Get Cisco Router BGP Info  ${router}
    Should Contain  ${value}  BGP neighbor is

Get Juniper Router BGP Info
    [Arguments]    ${router}
    ${params} =  Create Dictionary  custom_command=show bgp summary | display xml
    ${value} =    Execute Command  ${SandboxId}  ${router}  run_custom_command  ${params}
    [Return]  ${value}

Get Cisco Router BGP Info
    [Arguments]    ${router}
    ${params} =  Create Dictionary  custom_command=show ip bgp neighbor
    ${value} =    Execute Command  ${SandboxId}  ${router}  run_custom_command  ${params}

    [Return]  ${value}

Validate Router OSPF Neighbors
    [Arguments]    ${router}    ${neighbors}
    Log To Console  ${router}
    