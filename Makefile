lint_py:
	flake8 app/app.py

build: lint_py
	docker build -t dhwe/appy:latest -t dhwe/appy:v1.0 . # $(COMMIT_ID)

push:
	docker push --all-tags dhwe/appy

clean:
	docker rmi dhwe/appy:latest dhwe/appy:v1.0 # $(COMMIT_ID)

run_instance:
	aws --region eu-north-1 cloudformation create-stack --stack-name asg --template-body file://ec2_template.yaml --parameters ParameterKey=CommitID,ParameterValue=string --on-failure DO_NOTHING
