
# KEES aws docker

pip freeze > requirements.txt

aws ecr get-login-password --region us-east-1 --profile kees_account | docker login --username AWS --password-stdin 510219444800.dkr.ecr.us-east-1.amazonaws.com
docker build -t kees-django-backend -f Production_Dockerfile .
docker tag kees-django-backend:latest 510219444800.dkr.ecr.us-east-1.amazonaws.com/kees-django-backend:latest
docker push 510219444800.dkr.ecr.us-east-1.amazonaws.com/kees-django-backend:latest

aws ecs update-service  --service kees-django-backend --cluster kees --force-new-deployment --region us-east-1 --profile kees_account

docker run -p 8000:8000 -it kees-django-backend


# KEES UAT aws docker
pip freeze > requirements.txt

aws ecr get-login-password --region us-east-1 --profile kees_account | docker login --username AWS --password-stdin 510219444800.dkr.ecr.us-east-1.amazonaws.com
docker build -t uat-kees-django-backend -f Staging_Dockerfile .
docker tag uat-kees-django-backend:latest 510219444800.dkr.ecr.us-east-1.amazonaws.com/uat-kees-django-backend:latest
docker push 510219444800.dkr.ecr.us-east-1.amazonaws.com/uat-kees-django-backend:latest

aws ecs update-service  --service  staging-kees-django-backend --cluster kees --force-new-deployment --region us-east-1 --profile kees_account

docker run -p 8000:8000 -it kees-django-backend