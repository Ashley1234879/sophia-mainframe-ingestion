#!/usr/bin/env groovy
pipeline {
  agent any

  options {
    disableConcurrentBuilds()
  }


  environment {
    AWS_DEFAULT_REGION = 'ap-southeast-2'
	  PROJECT_ID = 'sophia'
    PROJECT_NAME = 'sophia-mainframe-ingestion'
	  ECR_ENDPOINT = 'https://847029211010.dkr.ecr.ap-southeast-2.amazonaws.com'
    CFN_ENVIRONMENT = 'datasvcsdev'
    CFN_ARTEFACT_ENVIRONMENT = 'artefact'
    VAULT_ADDR="https://active.vault.service.consul.a-sharedinfra.net:8200"
    VAULT_SKIP_VERIFY='true'
    VAULT_ENVIRONMENT='datasvcsdev'
    CFN_SOURCE_PROJECT_ID = 'sophia'
  }

  stages {
      stage('Initialize') {
      steps {
        // Set Environment Variables from GIT
        script {
          deleteDir()
          checkout scm
          echo 'Get Git commit ID'
          // Git commit id
          env['GIT_COMMIT_ID'] = sh (
            script: 'git rev-parse HEAD',
            returnStdout: true
          ).trim()

          echo 'Get committer email'
          // Git committer email
          env['GIT_COMMIT_EMAIL'] = sh (
            script: 'git --no-pager show -s --format=\'%ae\'',
            returnStdout: true
          ).trim()

          echo 'Get git repo'
          // Git committer email
          env['GIT_REPO'] = sh (
            script: 'git config --get remote.origin.url',
            returnStdout: true
          ).trim()

          echo 'Get committer author'
          // Git committer email
          env['GIT_AUTHOR'] = sh (
            script: 'git --no-pager show -s --format=\'%an\'',
            returnStdout: true
          ).trim()
        }
      }
    }
    stage('[DEV] Stack to create Inventory etl pipeline ECR Repo') {
      environment {
        CFN_ENVIRONMENT = 'artefact'
      }
      steps {
        script {
          withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "$CFN_SOURCE_PROJECT_ID-aws-${env.CFN_ENVIRONMENT}"]]) {
            docker.image("${ECR_HOST}/sharedtools/cfn_manage:latest").inside {
              sh './scripts/deploy_infra.sh'
            }
          }
        }
      }
    }
    stage('Building Docker Image: Inventory etl pipeline') {
      steps {
        script {
          node {
            checkout scm
            def dockerBuild = docker.build("${env.PROJECT_ID}/${env.PROJECT_NAME}:latest", "--no-cache --build-arg http_proxy=${env.http_proxy} --build-arg https_proxy=${env.https_proxy} --build-arg no_proxy=${env.no_proxy} -f ./Dockerfile .")
              withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
              credentialsId: "${env.PROJECT_ID}-aws-${env.CFN_ARTEFACT_ENVIRONMENT}"]]) {
              docker.withRegistry("${env.ECR_ENDPOINT}") {
                dockerBuild.push()
              }
            }
          }
        }
      }
    }
    stage('Confirm deployment to Prod?') {
      steps {
        timeout(time: 15, unit: 'MINUTES') {
          script {
            input (message: "Deploy to prod?")
          }
        }
      }
    }    
    // stage('Deploy sophia sales data mart ecr - PROD') {
    //   environment {
    //     CFN_ENVIRONMENT = 'artefact'
    //     ENVIRONMENT = 'prod'
    //   }
    //   steps {
    //     script {
    //       withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "${PROJECT_ID}-aws-${env.CFN_ENVIRONMENT}"]]) {
    //         docker.image("${ECR_HOST}/sharedtools/cfn_manage:latest").inside {
    //           sh './scripts/deploy_cloudformation.sh'
    //         }
    //       }
    //     }
    //   }
    // }
    // stage('Building Docker Image: Inventory data loading - PROD') {
    //   steps {
    //     script {
    //       node {
    //         checkout scm
    //         sh "find . -type f -print0 | xargs -0 sed -i 's/KSF_SOPHIA_DATA_INTELLIGENCE_HUB_DEV/KSF_SOPHIA_DATA_INTELLIGENCE_HUB_PROD/g'"
    //         sh "sed -i 's/sophia-inventory-dev/sophia-inventory-prod/g' sales_datamart_dag.py"
    //         def dockerBuild = docker.build("${env.PROJECT_ID}/${env.PROJECT_NAME}-prod:latest", "--no-cache --build-arg http_proxy=${env.http_proxy} --build-arg https_proxy=${env.https_proxy} --build-arg no_proxy=${env.no_proxy} -f ./Dockerfile .")
    //           withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
    //           credentialsId: "${env.PROJECT_ID}-aws-${env.CFN_ARTEFACT_ENVIRONMENT}"]]) {
    //           docker.withRegistry("${env.ECR_ENDPOINT}") {
    //             dockerBuild.push()
    //           }
    //         }
    //       }
    //     }
    //   }
    // }
  }
  // post {
  //   success {
  //     slackSend color: "good", channel: SLACK_NOTIFY_CHANNEL, message: ":tada: SUCCESS: Job - <${env.JOB_DISPLAY_URL}|${env.JOB_NAME} #${env.BUILD_NUMBER}>"
  //     echo "success"
  //   }
  //   failure {
  //     slackSend color: "danger", channel: SLACK_NOTIFY_CHANNEL, message: "@here: :fire: :fire_engine: :ambulance: FAILURE: Job - <${env.JOB_DISPLAY_URL}|${env.JOB_NAME} #${env.BUILD_NUMBER}>"
  //     echo "Failed"
  //   }
  //   unstable {
  //     slackSend color: "warning", channel: SLACK_NOTIFY_CHANNEL, message: "UNSTABLE: Job - <${env.JOB_DISPLAY_URL}|${env.JOB_NAME} #${env.BUILD_NUMBER}>"
  //     echo "unstable"
  //   }
  // }
}
