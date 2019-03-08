pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        echo 'Building artifacts'
      }

    }
    stage('testing bgp config') {
      steps {
        script {
          reservationId = startSandbox(duration: 20, name: 'Router test')
        }

        sh 'robot ./tests'
        stopSandbox(reservationId)

      }
    }
    stage('testing ospf config') {
      steps {
        script {
          reservationId = startSandbox(duration: 20, name: 'Router test')
        }

        sh 'robot ./tests'
        stopSandbox(reservationId)

      }
    }
  }
}