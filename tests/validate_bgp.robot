*** Settings ***
Library           OperatingSystem
Library           ../lib/SandboxLibrary.py  ${CloudShellURL}  ${User}  ${Password}  ${Domain}

*** Variables ***
${SandboxId}                 c5cd06a8-9244-45d7-a105-03bff43317f5
${CiscoRouter}               Juniper EX 4200
${CloudShellURL}             
${User}
${Password}     
${Domain}                    Demo Advanced
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
    Execute Command  ${SandboxId}  ${router}  showBGP
    Log To Console  ${SandboxId}

Validate Router OSPF Neighbors
    [Arguments]    ${router}    ${neighbors}
    Log To Console  ${router}
    