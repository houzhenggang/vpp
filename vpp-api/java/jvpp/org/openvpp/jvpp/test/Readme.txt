This package contains basic tests for jvpp. To run the tests:

- Make sure VPP is running
- From VPP's build-root/ folder execute:
  - sudo java -cp .:build-vpp-native/vpp-api/java/jvpp-1.0.0.jar org.openvpp.jvpp.test.ControlPingTest
  - sudo java -cp .:build-vpp-native/vpp-api/java/jvpp-1.0.0.jar org.openvpp.jvpp.test.FutureApiTest
  - sudo java -cp .:build-vpp-native/vpp-api/java/jvpp-1.0.0.jar org.openvpp.jvpp.test.CallbackApiTest

Available tests:
ControlPingTest - Simple test executing a single control ping using low level JVpp APIs
CallbackApiTest - Similar to ControlPingTest, invokes more complex calls (e.g. interface dump) using low level JVpp APIs
FutureApiTest - Execution of more complex calls using Future based JVpp facade
CallbackJVppFacadeTest - Execution of more complex calls using Callback based JVpp facade