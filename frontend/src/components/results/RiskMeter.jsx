function RiskMeter({ score = 0 }) {
    const color =
        score >= 80
            ? "bg-red-500"
            : score >= 60
            ? "bg-orange-500"
            : score >= 40
            ? "bg-yellow-500"
            : "bg-green-500";

    const label =
        score >= 80
            ? "HIGH"
            : score >= 60
            ? "MEDIUM"
            : score >= 40
            ? "LOW"
            : "SAFE";

    return (
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <h2 className="text-xl font-semibold mb-6">
                Overall Risk Score
            </h2>

            <div className="w-full h-5 bg-slate-700 rounded-full overflow-hidden">
                <div
                    className={`${color} h-full transition-all duration-700`}
                    style={{ width: `${score}%` }}
                />
            </div>

            <div className="flex justify-between items-center mt-6">
                <h1 className="text-5xl font-bold">
                    {score}%
                </h1>

                <span className="px-4 py-2 rounded-full bg-slate-700">
                    {label}
                </span>
            </div>
        </div>
    );
}

export default RiskMeter;