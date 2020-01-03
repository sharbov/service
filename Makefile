VERSION = 1.0.0

all: static unittests image integration build/service-client-1.0.0.tar.gz

## format: auto format the code
format:
	black service tests --line-length=79

## static: run static code analysis
static: format
	flake8 service
	pylint service -j 4 -E --rcfile=.pylintrc.ini

## unittests: run the unittests & generate reports
unittests:
	mkdir -p ./build
	nose2 --config=tests/ut/nose2.cfg --project-directory . --verbose  $(TEST)
	coverage html --fail-under=10 -d build/coverage
	# ====== Coverage report: ======
	@echo file://$(HOST_PWD)/build/coverage/index.html

## image: build the service image
image:
	docker build -t service .

## up: run the service stack using docker-compose
up: image
	docker-compose -p run \
     -f compose/docker-compose.core.yml \
     -f compose/docker-compose.tracing.yml \
     -f compose/docker-compose.efk.yml \
     -f compose/docker-compose.metrics.yml \
     -f compose/docker-compose.flower.yml \
     build

	docker-compose -p run \
     -f compose/docker-compose.core.yml \
     -f compose/docker-compose.tracing.yml \
     -f compose/docker-compose.efk.yml \
     -f compose/docker-compose.metrics.yml \
     -f compose/docker-compose.flower.yml \
     up

## down: stop the service stack using docker-compose
down:
	docker-compose -p run \
     -f compose/docker-compose.core.yml \
     -f compose/docker-compose.tracing.yml \
     -f compose/docker-compose.efk.yml \
     -f compose/docker-compose.metrics.yml \
     -f compose/docker-compose.flower.yml \
     down

## integration: run the integration tests
integration: image build/service-client-1.0.0.tar.gz
	mkdir -p build/integration/
	PYTHONPATH=PYTHONPATH:./build/client \
	nose2 --config=tests/integration/nose2.cfg --project-directory . --verbose -F $(TEST)

## build/service-client-1.0.0.tar.gz: generate python client package based on the spec file
build/service-client-1.0.0.tar.gz: service/spec.yaml
	mkdir -p ./build
	rm -rf ./build/client

	# Generate python client package based on the spec file
	docker run --rm \
		-u $(shell id -u $(USER)) \
		-v $(HOST_PWD)/build:/local/out \
		-v $(HOST_PWD)/service/spec.yaml:/spec.yaml:ro \
		openapitools/openapi-generator-cli:v4.3.0 generate \
		-i /spec.yaml \
		-g python \
		-o /local/out/client \
		--api-package service_api \
		--package-name service_client \
		--artifact-version $(VERSION)

	# Fix client imports bug (TODO: Open a bug to openapi-generator-cli)
	find build/client/service_client -type f -exec \
		sed -i 's/from service_api/from service_client.service_api/g' {} +

	cd ./build/client && python setup.py sdist --dist-dir ../

## clean: clean generated files
clean:
	rm -rf service.egg-info .coverage* build

## help: show makefile actions
help : Makefile
	@printf '\nMakeflie Actions:\n\n'
	@sed -n 's/^##//p' $<
