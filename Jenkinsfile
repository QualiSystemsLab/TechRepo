pipeline {
  agent any
  stages {
    stage('testing') {
      steps {
        withSandbox(name: 'Router test', maxDuration: 20, timeout: 20, params: ' ', sandboxName: ' ', sandboxDomain: ' ') {
          echo 'hello'
        }

      }
    }
  }
}