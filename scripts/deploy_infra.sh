#!/bin/bash

# http://blog.kablamo.org/2015/11/08/bash-tricks-eux/
set -euxo pipefail
cd "$(dirname "$0")/.."

# shellcheck disable=SC1091
. "scripts/stack_name_vars.sh"

#ECR
cfn_manage deploy-stack \
  --stack-name "$CFN_ECR_STACK" \
  --template-file "cloudformation/templates/ecr.yml" \
  --role-name "$NONPRIV_ROLE_NAME"
