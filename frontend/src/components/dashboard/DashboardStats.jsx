import {
    FaBug,
    FaDatabase,
    FaExclamationTriangle,
    FaFileAlt,
} from "react-icons/fa";

import StatsCard from "./StatsCard";

function DashboardStats({ statistics, loading }) {
    return (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

            <StatsCard
                loading={loading}
                title="Total Scans"
                value={statistics?.total_scans ?? 0}
                subtitle="Completed analyses"
                icon={<FaBug className="text-blue-400" />}
                color="bg-slate-800"
            />

            <StatsCard
                loading={loading}
                title="Critical Vulnerabilities"
                value={statistics?.critical_vulnerabilities ?? 0}
                subtitle="Require immediate action"
                icon={<FaExclamationTriangle className="text-red-500" />}
                color="bg-gradient-to-br from-red-900 to-red-700"
            />

            <StatsCard
                loading={loading}
                title="Reports Generated"
                value={statistics?.reports_generated ?? 0}
                subtitle="Professional PDF reports"
                icon={<FaFileAlt className="text-green-400" />}
                color="bg-gradient-to-br from-emerald-900 to-green-700"
            />

            <StatsCard
                loading={loading}
                title="Knowledge Base"
                value={statistics?.knowledge_base_entries ?? 0}
                subtitle="AI security rules"
                icon={<FaDatabase className="text-purple-400" />}
                color="bg-gradient-to-br from-indigo-900 to-purple-700"
            />

        </div>
    );
}

export default DashboardStats;