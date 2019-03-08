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

        sh 'robot --nostatusrc --outputdir ./robot_reports/integration -i bgp ./tests'
        stopSandbox(reservationId)

      }
    }
    stage('testing ospf config') {
      steps {
        script {
          reservationId = startSandbox(duration: 20, name: 'Router test')
        }

        sh 'robot --nostatusrc --outputdir ./robot_reports/integration -i ospf ./tests'
        stopSandbox(reservationId)

      }
    }

    stage('publish test results ') {
      steps{
        
        step([$class : 'RobotPublisher',
            outputPath : 'robot_reports',
            reportFileName      : '**/report.html',
            logFileName         : '**/log.html',
            outputFileName : "*.xml",
            disableArchiveOutput : false,
            passThreshold : 100,
            unstableThreshold: 95.0,
            otherFiles : "**/*.png,**/*.jpg",])
      }
    }
  }
}