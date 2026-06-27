$repo = "https://github.com/Guruprasad-Shrinivas/AI-Tester-Blueprint-3x"
$branch = "AI-Tester-Blueprint-3x"
$message = "[done]"

if (-not (Test-Path .git)) {
    git init
}

git checkout -B $branch 2>$null
if ($LASTEXITCODE -ne 0) {
    git checkout $branch 2>$null
}

git add .
git commit -m $message

git remote remove origin 2>$null
git remote add origin $repo 2>$null

git push -u origin $branch
