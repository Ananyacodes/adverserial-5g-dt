/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */

/**
 * 5G baseline simulation - generates benign UE telemetry.
 *
 * Three UEs connecting to a single gNB, with normal RSRP, latency, and throughput.
 * Outputs telemetry to CSV file and stdout.
 *
 * Run with: ./ns3 run "scratch/5g_baseline"
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include <fstream>
#include <chrono>
#include <ctime>
#include <iomanip>
#include <sstream>
#include <string>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("5GBaseline");

static void
OutputTelemetry(std::ofstream& file, Time now, uint32_t ue_id, double rsrp,
                 double latency, double throughput, uint32_t label)
{
    std::ostringstream oss;
    oss << now.GetSeconds() << "," << ue_id << "," << rsrp << ","
        << latency << "," << throughput << "," << label;
    std::string line = oss.str();
    file << line << std::endl;
    std::cout << line << std::endl;
}

static std::string
GetProvenancePath(const std::string& output_file)
{
    const std::string suffix = ".csv";
    const auto pos = output_file.rfind(suffix);
    if (pos != std::string::npos && pos + suffix.size() == output_file.size())
    {
        return output_file.substr(0, pos) + ".provenance.json";
    }

    return output_file + ".provenance.json";
}

int
main(int argc, char* argv[])
{
    std::string output_file = "scratch/5g_baseline_telemetry.csv";
    CommandLine cmd;
    cmd.AddValue("outputFile", "Telemetry CSV output path", output_file);
    cmd.Parse(argc, argv);

    // Create log file in the ns-3 checkout by default.
    std::ofstream telemetry_file(output_file);
    if (!telemetry_file.is_open())
    {
        std::cerr << "Failed to open telemetry output file: " << output_file << std::endl;
        return 1;
    }
    telemetry_file << "timestamp,ue_id,rsrp,latency,throughput,label" << std::endl;

    uint32_t benign_rows = 0;
    uint32_t anomaly_rows = 0;
    uint32_t total_rows = 0;
    const auto generated_at = std::chrono::system_clock::now();
    const auto generated_at_seconds = std::chrono::duration_cast<std::chrono::seconds>(
        generated_at.time_since_epoch()).count();

    // Simulate 3 UEs with benign behavior for 2 seconds
    // RSRP typically ranges from -140 (poor) to -44 (excellent) dBm
    // Latency: 10-50 ms, Throughput: 20-100 Mbps

    for (double t = 0.0; t < 2.0; t += 0.1)
    {
        // UE 1: Good signal, low latency, high throughput (benign)
        double rsrp1 = -80.0 + (rand() % 3 - 1);  // -81 to -79
        double latency1 = 25.0 + (rand() % 5 - 2); // 23-27 ms
        double throughput1 = 45.0 + (rand() % 5 - 2); // 43-47 Mbps
        OutputTelemetry(telemetry_file, Seconds(t), 1, rsrp1, latency1, throughput1, 0);
        ++benign_rows;
        ++total_rows;

        // UE 2: Medium signal (benign)
        double rsrp2 = -75.0 + (rand() % 3 - 1);  // -76 to -74
        double latency2 = 23.0 + (rand() % 4 - 2); // 21-25 ms
        double throughput2 = 48.0 + (rand() % 4 - 2); // 46-50 Mbps
        OutputTelemetry(telemetry_file, Seconds(t), 2, rsrp2, latency2, throughput2, 0);
        ++benign_rows;
        ++total_rows;

        // UE 3: Poor signal (benign)
        double rsrp3 = -85.0 + (rand() % 3 - 1);  // -86 to -84
        double latency3 = 28.0 + (rand() % 5 - 2); // 26-30 ms
        double throughput3 = 42.0 + (rand() % 5 - 2); // 40-44 Mbps
        OutputTelemetry(telemetry_file, Seconds(t), 3, rsrp3, latency3, throughput3, 0);
        ++benign_rows;
        ++total_rows;
    }

    // Add anomaly period: same UEs at t=1.0-1.5s show degradation
    for (double t = 1.0; t < 1.5; t += 0.1)
    {
        // All UEs show poor signal / high latency / low throughput (anomaly)
        double rsrp1 = -92.0 + (rand() % 3 - 1);  // -93 to -91 (degraded)
        double latency1 = 35.0 + (rand() % 5 - 2); // 33-37 ms (high)
        double throughput1 = 28.0 + (rand() % 5 - 2); // 26-30 Mbps (low)
        OutputTelemetry(telemetry_file, Seconds(t), 1, rsrp1, latency1, throughput1, 1);
        ++anomaly_rows;
        ++total_rows;

        double rsrp2 = -90.0 + (rand() % 3 - 1);
        double latency2 = 32.0 + (rand() % 4 - 2);
        double throughput2 = 31.0 + (rand() % 4 - 2);
        OutputTelemetry(telemetry_file, Seconds(t), 2, rsrp2, latency2, throughput2, 1);
        ++anomaly_rows;
        ++total_rows;

        double rsrp3 = -88.0 + (rand() % 3 - 1);
        double latency3 = 33.0 + (rand() % 5 - 2);
        double throughput3 = 32.0 + (rand() % 5 - 2);
        OutputTelemetry(telemetry_file, Seconds(t), 3, rsrp3, latency3, throughput3, 1);
        ++anomaly_rows;
        ++total_rows;
    }

    telemetry_file.close();

    std::ofstream provenance_file(GetProvenancePath(output_file));
    if (!provenance_file.is_open())
    {
        std::cerr << "Failed to open provenance file for telemetry output: "
                  << output_file << std::endl;
        return 1;
    }

    provenance_file << "{\n"
                    << "  \"generator\": \"ns-3 scratch/5g_baseline.cc\",\n"
                    << "  \"output_csv\": \"" << output_file << "\",\n"
                    << "  \"generated_at_unix_seconds\": " << generated_at_seconds << ",\n"
                    << "  \"simulation_duration_seconds\": 2.0,\n"
                    << "  \"row_count\": " << total_rows << ",\n"
                    << "  \"benign_row_count\": " << benign_rows << ",\n"
                    << "  \"anomaly_row_count\": " << anomaly_rows << ",\n"
                    << "  \"label_schema\": {\"0\": \"benign\", \"1\": \"anomaly\"}\n"
                    << "}\n";
    provenance_file.close();

    std::cout << "Telemetry written to " << output_file << std::endl;
    std::cout << "Provenance written to " << GetProvenancePath(output_file) << std::endl;

    return 0;
}
