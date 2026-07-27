const recommendations = [
    "Enable Content Security Policy (CSP).",
    "Sanitize all user supplied inputs.",
    "Use parameterized SQL queries.",
    "Enable secure HTTP headers.",
    "Upgrade outdated third-party libraries.",
];

function RecentRecommendations() {

    return (

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">

            <h2 className="text-xl font-semibold mb-5">
                Latest AI Recommendations
            </h2>

            <div className="space-y-4">

                {recommendations.map((item, index) => (

                    <div
                        key={index}
                        className="bg-slate-900 rounded-lg p-4 border border-slate-700"
                    >

                        {item}

                    </div>

                ))}

            </div>

        </div>

    );

}

export default RecentRecommendations;