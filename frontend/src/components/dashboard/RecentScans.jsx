const riskColor = {
    Critical: "text-red-500",
    High: "text-orange-400",
    Medium: "text-yellow-400",
    Low: "text-green-400",
};

function RecentScans({ scans, loading }) {

    if (loading) {
        return (
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 animate-pulse h-80" />
        );
    }

    if (!scans.length) {

        return (

            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">

                <h2 className="text-xl font-semibold">
                    Recent Scans
                </h2>

                <p className="text-slate-400 mt-6">
                    No scans available.
                </p>

            </div>

        );

    }

    return (

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">

            <h2 className="text-xl font-semibold mb-5">
                Recent Scans
            </h2>

            <table className="w-full">

                <thead>

                    <tr className="border-b border-slate-700 text-slate-400">

                        <th className="text-left py-3">
                            Scan ID
                        </th>

                        <th className="text-left">
                            Risk
                        </th>

                        <th className="text-left">
                            Date
                        </th>

                    </tr>

                </thead>

                <tbody>

                    {scans.slice(0, 5).map((scan) => {

                        const risk =
                            scan.summary?.overall_risk ??
                            "Low";

                        return (

                            <tr
                                key={scan.scan_id}
                                className="border-b border-slate-700 hover:bg-slate-700/40"
                            >

                                <td className="py-4 font-medium">
                                    {scan.scan_id}
                                </td>

                                <td
                                    className={
                                        riskColor[risk] ??
                                        "text-green-400"
                                    }
                                >
                                    {risk}
                                </td>

                                <td>
                                    {new Date(
                                        scan.created_at
                                    ).toLocaleDateString()}
                                </td>

                            </tr>

                        );

                    })}

                </tbody>

            </table>

        </div>

    );

}

export default RecentScans;