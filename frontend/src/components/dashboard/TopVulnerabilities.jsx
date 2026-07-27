const vulnerabilities = [
    {
        name: "SQL Injection",
        severity: "Critical",
        count: 8,
    },
    {
        name: "Cross Site Scripting",
        severity: "High",
        count: 15,
    },
    {
        name: "Security Headers Missing",
        severity: "Medium",
        count: 20,
    },
    {
        name: "Information Disclosure",
        severity: "Low",
        count: 12,
    },
];

const colors = {
    Critical: "text-red-500",
    High: "text-orange-400",
    Medium: "text-yellow-400",
    Low: "text-green-400",
};

function TopVulnerabilities() {

    return (

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">

            <h2 className="text-xl font-semibold mb-5">
                Top Vulnerabilities
            </h2>

            <div className="space-y-4">

                {vulnerabilities.map((item) => (

                    <div
                        key={item.name}
                        className="flex justify-between border-b border-slate-700 pb-3"
                    >

                        <div>

                            <p className="font-semibold">
                                {item.name}
                            </p>

                            <span className={colors[item.severity]}>
                                {item.severity}
                            </span>

                        </div>

                        <span className="text-2xl font-bold">
                            {item.count}
                        </span>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default TopVulnerabilities;