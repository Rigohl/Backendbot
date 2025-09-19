<#
Temporarily disable pre-commit hooks for local commits by setting
`GIT_PARAMS` or by creating a lightweight wrapper. This script creates
a git config alias `commit-noverify` that runs `git commit --no-verify`.

Use: `.	emplates/disable_precommit.ps1` or run interactively.
#>
param()

Write-Host "Creating git alias 'commit-noverify' -> 'commit --no-verify'"
git config --local alias.commit-noverify "commit --no-verify"
Write-Host "Alias created. Use 'git commit-noverify -m \"msg\"' to commit without hooks"
