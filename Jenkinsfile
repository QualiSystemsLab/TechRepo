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

        step([$class : 'RobotPublisher',
        outputPath : '~/output',
        outputFileName : "*.xml",
        disableArchiveOutput : false,
        passThreshold : 100,
        unstableThreshold: 95.0,
        otherFiles : "*.png",])

        sh 'robot -i bgp --outputdir ~/output ./tests'
        stopSandbox(reservationId)

      }
    }
    stage('testing ospf config') {
      steps {
        script {
          reservationId = startSandbox(duration: 20, name: 'Router test')
        }

        sh 'robot -i ospf --outputdir ~/output ./tests'
        stopSandbox(reservationId)

      }
    }
  }
}