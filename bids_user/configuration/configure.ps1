Param(
    [string]$jbossZip = ""
)

if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Host "You need the at least version 5 of Powershell to run this script"
    return
}

# Get the project root and where the Jboss will be/is installed
$bidsHome = (Get-Item $PSScriptRoot).Parent.FullName
$jbossHome = $bidsHome + "\" + "jboss-eap-6.4\"

# unzip the JBoss archive is given as argument
if ($jbossZip -ne "" ) {
    Expand-Archive -Path $jbossZip -DestinationPath $bidsHome -Force
}

# Do some simple textual substitutions. 
$bidsHome = $bidsHome -replace '\\', '/'

$standaloneXml = Get-Content ($bidsHome + "/configuration/standalone.xml") -Encoding UTF8
$standaloneXml = $standaloneXml -replace '##SAS_BIDS_HOME##', $bidsHome 

$standaloneXml | Out-File ($jbossHome + "standalone\configuration\standalone.xml") -Encoding ascii 

$crewwebProperties = Get-Content ($bidsHome + "/configuration/crewweb.properties") -Encoding UTF8
$crewwebProperties = $crewwebProperties -replace '##SAS_BIDS_HOME##', $bidsHome

$crewwebProperties | Out-File ($bidsHome + "/jboss-files/resources/crewweb.properties") -Encoding ascii