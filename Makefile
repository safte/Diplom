lint_py:
	flake8 app/app.py

login:
	echo '$(DOCKERHUB_CREDENTIALS_PSW)' | docker login -u $(DOCKERHUB_CREDENTIALS_USR) --password-stdin

build: lint_py login 
	docker build -t dhwe/appy:latest -t dhwe/appy:v1.0 . # $(COMMIT_ID)

push:
	docker push --all-tags dhwe/appy

clean:
	docker rmi dhwe/appy:latest dhwe/appy:v1.0 # $(COMMIT_ID)

pull:
	docker pull dhwe/appy:latest

run:
	docker run -d -p 5000:5000 dhwe/appy:latest
