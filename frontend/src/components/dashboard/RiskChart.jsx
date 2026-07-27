import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    ResponsiveContainer,
    Legend,
} from "recharts";

const COLORS = [
    "#ef4444",
    "#f97316",
    "#eab308",
    "#22c55e",
];

function RiskChart({ statistics, loading }) {

    if (loading) {
        return (
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 h-96 animate-pulse" />
        );
    }

    const severity = statistics?.severity_distribution ?? {};

    const data = [
        {
            name: "Critical",
            value: severity.critical ?? 0,
        },
        {
            name: "High",
            value: severity.high ?? 0,
        },
        {
            name: "Medium",
            value: severity.medium ?? 0,
        },
        {
            name: "Low",
            value: severity.low ?? 0,
        },
    ];

    return (
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">

            <h2 className="text-xl font-semibold mb-6">
                Vulnerability Distribution
            </h2>

            <div className="h-80">

                <ResponsiveContainer>

                    <PieChart>

                        <Pie
                            data={data}
                            dataKey="value"
                            nameKey="name"
                            outerRadius={105}
                            label
                        >
                            {data.map((entry, index) => (
                                <Cell
                                    key={index}
                                    fill={COLORS[index]}
                                />
                            ))}
                        </Pie>

                        <Tooltip />
                        <Legend />

                    </PieChart>

                </ResponsiveContainer>

            </div>

        </div>
    );
}

export default RiskChart;