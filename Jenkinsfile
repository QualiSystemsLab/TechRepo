pipeline {
  agent any
  environment {
    CS_CRED = credentials('cslive') 

  }
  stages {
    stage('build') {
      steps {
        echo 'Building artifacts'
      }

    }
    stage('testing bgp config') {
      steps {

        script {
            try{
                ReservationId = startSandbox(duration: 20, name: 'Router BGP OSPF Testing', 
                                       params: 'Router Configuration File Set=BGP;Cisco Router Configuration File=cisco_bgp.config;Juniper Router Configuration File=juniper_bgp.config')
            }
            catch (Exception e){
                print e.getClass()
                print e.Message


            }
  
        }

        sh "robot -x bgp_config --nostatusrc --outputdir ./robot_reports -v SandboxId:$ReservationId -v CloudShellURL:https://demo.quali.com:8443 -v User:$CS_CRED_USR -v Password:$CS_CRED_PSW -i bgp ./tests"
        stopSandbox(ReservationId)

      }
    }
    // stage('testing ospf config') {
    //   steps {
    //     script {
    //       reservationId = startSandbox(duration: 20, name: 'Router test')
    //     }

    //     sh 'robot -x ospf_config --nostatusrc --outputdir ./robot_reports -i ospf ./tests'
    //     stopSandbox(reservationId)

    //   }
    // }

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
  
  post{
      always {
          junit 'robot_reports/*.xml'
          archiveArtifacts artifacts: 'robot_reports/*.html', fingerprint: true
      }
  }
}