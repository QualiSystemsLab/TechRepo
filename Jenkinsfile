pipeline {
  agent any
  stages {
    stage('testing') {
      steps {
        script {
          reservationId = startSandbox(duration: 20, name: 'Router test')
        }

        echo 'test'
      }
    }
  }
}