pipeline {
  agent any
  stages {
    stage('integration') {
      steps {
        startSandbox(name: 'Router test', duration: 20, timeout: 20)
        echo 'hello'
      }
    }
  }
}