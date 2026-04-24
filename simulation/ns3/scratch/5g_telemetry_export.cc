// This is the main ns-3 simulation script
// It defines the network topology, runs the simulation,
// and exports telemetry to a socket or file

#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/nr-module.h"

using namespace ns3;

int main(int argc, char* argv[]) {
    // Setup 5G nodes
    NodeContainer gNbs;
    gNbs.Create(5);  // 5 base stations
    
    NodeContainer ues;
    ues.Create(50);  // 50 user devices
    
    // Install 5G stack
    NrHelper nrHelper;
    nrHelper.SetAttribute("Numerology", UintegerValue(1));
    nrHelper.Install(gNbs, ues);
    
    // Attach telemetry tracing
    Config::ConnectWithoutContext(
        "/NodeList/*/DeviceList/*/NrUePhy/ReportUeMeasurements",
        MakeCallback(&TelemetryCallback));
    
    // Run simulation for 600 seconds
    Simulator::Stop(Seconds(600.0));
    Simulator::Run();
    Simulator::Destroy();
    
    return 0;
}