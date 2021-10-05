lint_py:
	flake8 app/app.py

build: lint_py
	docker build -t dhwe/appy:latest -t dhwe/appy:$(GIT_COMMIT) .

push:
	docker push --all-tags dhwe/appy

clean:
	docker rmi dhwe/appy:latest dhwe/appy:$(GIT_COMMIT)

update_stack:
	aws --region eu-west-1 cloudformation update-stack --stack-name $(STACK_NAME) --template-body file://cf_template.yaml --capabilities CAPABILITY_IAM --parameters ParameterKey=CommitID,ParameterValue=$(GIT_COMMIT) ParameterKey=VPCCIDRBlock,ParameterValue=$(VPC_CIDR_BLOCK) ParameterKey=SubnetACIDRBlock,ParameterValue=$(SUBNET_A_CIDR_BLOCK) ParameterKey=SubnetBCIDRBlock,ParameterValue=$(SUBNET_B_CIDR_BLOCK)
