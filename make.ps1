
###################3
[CmdletBinding()]
Param(
    [Parameter(Mandatory = $True, Position = 1)]
    [string]$command
)

$Script:BROWSER_PYSCRIPT = "
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open(""file://"" + pathname2url(os.path.abspath(sys.argv[1])))
"
$Script:PRINT_HELP_PYSCRIPT = "
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print(""%-20s %s"" % (target, help))
"

function help() {
    Get-Help -Name "make"
#	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)
}

<#
.Description
Make file for Nuvoton ISP
#>
function make($command) {

}

<#
.Description
Remove all build, test, coverage and Python artifacts
#>
function clean() {
    cleanBuild
    cleanPyc
    cleanTest
}

<#
.Description
Remove build artifacts
#>
function cleanBuild() {
    $paths = @(".\build", ".\dist", ".\.eggs", ".\*.egg-info", ".\*.egg")
    foreach ($path in $paths) {
        if (Test-Path $path) 
        {
            Remove-Item $path -Recurse
        }
    }
}

<#
.Description
Remove Python file artifacts
#>
function cleanPyc() {
    $paths = @(".\*.pyc", ".\*.pyc", ".\*.pyo", ".\*~", ".\__pycache__")
    foreach ($path in $paths) {
        if (Test-Path $path)
        {
            Remove-Item $path -Recurse
        }
    }
}

<#
.Description
Remove test and coverage artifacts
#>
function cleanTest() {
    $paths = @(".\.tox", ".\.coverage", ".\.htmlcov", ".\.pytest_cache")
    foreach ($path in $paths) {
        if (Test-Path $path)
        {
            Remove-Item $path -Recurse
        }
    }
}

<#
.Description
Check style with flake8
#>
function lint() {
    poetry run flake8 src\nuvoton_isp tests
}

<#
.Description
Run tests quickly with the default Python
#>
function test() {
    poetry run pytest
}

<#
.Description
Run tests on every Python version with tox
#>
function testAll() {
    poetry run tox
}

<#
.Description
Check code coverage quickly with the default Python
#>
function coverage() {
    poetry run coverage run --source src\nuvoton_isp -m pytest
    poetry run coverage report -m
    poetry run coverage html
    poetry run python -c $Script:BROWSER_PYSCRIPT(htmlcov\index.html)
}

<#
Generate Sphinx HTML documentation, including API docs
#>
function docs(){
    if (Test-Path ".\docs\nuvoton_isp.rst") { Remove-Item ".\docs\nuvoton_isp.rst" -Force }
    if (Test-Path ".\docs\modules.rst") { Remove-Item ".\docs\modules.rst" -Force }
    poetry run sphinx-apidoc -o docs\ src\nuvoton_isp
    poetry run .\docs\make.bat clean
    poetry run .\docs\make.bat html
    poetry run python $Script:BROWSER_PYSCRIPT(.\docs\_build\html\index.html)
}

<#
Compile the docs watching for changes
#>
function servedocs() {
    docs
    poetry run watchmedo shell-command -p '.\docs\*.rst'; poetry run .\docs\make.bat html -R -D
}

<#
Package and upload a release
#>
function release() {
    dist
    poetry publish
}

<#
Builds source and wheel package
#>
function dist() {
    clean
    poetry build
}

<#
Install the package to the active Python's site-packages
#>
function install() {
    clean
    poetry install
}

function bumpversionMajor {
    poetry run bump2version major
}

function bumpversionMinor {
    poetry run bump2version minor
}

function bumpversionPatch {
    poetry run bump2version patch
}
    
switch ($command) {
    install { install; break }
    dist { dist; break }
    release { release; break }
    servedocs { servedocs; break }
    docs { docs; break }
    coverage { coverage; break }
    test { test; break }
    test-all { testAll; break }
    lint { lint; break }
    clean-test { cleanTest; break }
    clean-pyc { cleanPyc; break }
    clean-build { cleanBuild; break }
    clean { clean; break }
    help { help; break }
    bumpversion-major { bumpversionMajor; break }
    bumpversion-minor { bumpversionMinor; break }
    bumpversion-patch { bumpversionPatch; break }
    Default {}
}