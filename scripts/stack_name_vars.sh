#!/bin/bash
if [[ -z "${STACK_SUFFIX-}" ]]; then
  # Jenkins - Multibranch Pipelines
  if [[ -n "${BRANCH_NAME-}" ]]; then
    if [[ "$BRANCH_NAME" != "master" ]]; then
      STACK_SUFFIX="-${BRANCH_NAME}"
    else
      STACK_SUFFIX=""
    fi
  # GNU/UNIX
  elif [[ -n "${USER-}" ]]; then
    STACK_SUFFIX="-${USER}"
  # Windows - Git Bash
  elif [[ -n "${USERNAME-}" ]]; then
    STACK_SUFFIX="-${USERNAME}"
  else
    echo "Could not cleanly determine stack suffix!" 1>&2
    exit 1
  fi
  STACK_SUFFIX=$(echo -n "$STACK_SUFFIX" | tr '[:upper:]' '[:lower:]')
fi

CFN_RAND_STRING="$(date '+%s' | base64)"
if [[ "${BRANCH_NAME-}" == 'master' ]]; then
  export CFN_MASTER_BRANCH='true'
else
  export CFN_MASTER_BRANCH='false'
fi

# TODO
export CFN_BRANCH_NAME="$BRANCH_NAME"
export CFN_BUILD_NUMBER="$BUILD_NUMBER"
export CFN_STACK_SUFFIX="${STACK_SUFFIX-}"
export CFN_IMAGE_RELEASE="${CFN_IMAGE_RELEASE:-latest}"

#Env
export CFN_SOURCE_PROJECT_ID="sophia"

#Vars
export CFN_TEMPLATE_DIR="cloudformation/templates"
export NONPRIV_ROLE_NAME="infra-cfnrole-sophia-nonprivileged"
export COMMON_PARAMS_FILE="cloudformation/params/${CFN_ENVIRONMENT}/${AWS_DEFAULT_REGION}.yml"

#ECR
export CFN_ECR_STACK="sophia-inventory-etl-ecr-${CFN_ENVIRONMENT}"
export CFN_RAND_STRING
