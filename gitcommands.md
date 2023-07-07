
git add .
git commit -m "ABC"
git push origin cms

git checkout production
git pull origin master
git push origin production
git checkout master
