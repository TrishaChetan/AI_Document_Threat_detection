import { useLocation, Navigate } from "react-router-dom";

import RiskMeter from "../components/results/RiskMeter";
import SummaryCard from "../components/results/SummaryCard";
import VulnerabilityCard from "../components/results/VulnerabilityCard";
import RecommendationCard from "../components/results/RecommendationCard";
import ReportDownload from "../components/results/ReportDownload";

function Results() {
    const { state } = useLocation();

    if (!state?.result) {
        return <Navigate to="/upload" replace />;
    }

    const result = state.result;

    const summary = result.summary || result.scan?.summary || {};

    const riskScore =
        summary.overall_risk_score ??
        summary.risk_score ??
        0;

    const vulnerabilities = result.ai_recommendations || [];

    return (
        <div className="space-y-8">

            <div className="flex justify-between items-center">

                <div>
                    <h1 className="text-4xl font-bold">
                        Scan Results
                    </h1>

                    <p className="text-slate-400 mt-2">
                        AI Powered Vulnerability Assessment
                    </p>
                </div>

                <ReportDownload report={result.pdf_report} />

            </div>

            <div className="grid md:grid-cols-3 gap-6">

                <SummaryCard
                    title="Scan ID"
                    value={result.scan_id}
                />

                <SummaryCard
                    title="Status"
                    value={result.status}
                />

                <SummaryCard
                    title="Total Vulnerabilities"
                    value={summary.total_vulnerabilities ?? vulnerabilities.length}
                />

            </div>

            <RiskMeter score={riskScore} />

            <div>

                <h2 className="text-3xl font-bold mb-6">
                    Vulnerabilities
                </h2>

                <div className="space-y-6">

                    {vulnerabilities.map((item, index) => (

                        <VulnerabilityCard
                            key={index}
                            vulnerability={item}
                        />

                    ))}

                </div>

            </div>

            <div>

                <h2 className="text-3xl font-bold mb-6">
                    AI Recommendations
                </h2>

                <div className="space-y-5">

                    {vulnerabilities.map((item, index) => (

                        <RecommendationCard
                            key={index}
                            recommendation={item}
                        />

                    ))}

                </div>

            </div>

        </div>
    );
}

export default Results;