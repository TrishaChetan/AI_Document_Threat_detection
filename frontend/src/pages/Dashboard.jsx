import { useEffect, useState } from "react";

import DashboardStats from "../components/dashboard/DashboardStats";
import KnowledgeStats from "../components/dashboard/KnowledgeStats";
import RecentScans from "../components/dashboard/RecentScans";
import RiskChart from "../components/dashboard/RiskChart";
import TopVulnerabilities from "../components/dashboard/TopVulnerabilities";
import RecentRecommendations from "../components/dashboard/RecentRecommendations";
import SystemHealth from "../components/dashboard/SystemHealth";

import {
    getHistory,
    getStatistics,
} from "../api/api";

function Dashboard() {

    const [statistics, setStatistics] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {

        const loadDashboard = async () => {

            try {

                const [stats, scans] = await Promise.all([
                    getStatistics(),
                    getHistory(),
                ]);

                setStatistics(stats);
                setHistory(scans);

            } catch (err) {
                console.error(err);
            }

            setLoading(false);

        };

        loadDashboard();

    }, []);

    return (

        <div className="space-y-8">

            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center">

                <div>

                    <h1 className="text-4xl font-bold">
                        Security Dashboard
                    </h1>

                    <p className="text-slate-400 mt-2">
                        AI Powered Web Vulnerability Assessment Platform
                    </p>

                </div>

                <div className="mt-4 lg:mt-0">

                    <div className="bg-green-600 px-5 py-2 rounded-full font-semibold shadow-lg">

                        ● System Online

                    </div>

                </div>

            </div>

            <DashboardStats
                statistics={statistics}
                loading={loading}
            />

            <div className="grid xl:grid-cols-3 gap-6">

                <div className="xl:col-span-2">

                    <RiskChart
                        statistics={statistics}
                        loading={loading}
                    />

                </div>

                <KnowledgeStats
                    statistics={statistics}
                    loading={loading}
                />

            </div>

            <RecentScans
                scans={history}
                loading={loading}
            />
            <div className="grid xl:grid-cols-2 gap-6">

                 <TopVulnerabilities />

                 <RecentRecommendations />

           </div>

<SystemHealth />

        </div>

    );

}

export default Dashboard;