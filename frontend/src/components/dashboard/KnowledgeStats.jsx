import {
    FaDatabase,
    FaBug,
    FaShieldAlt,
    FaRobot,
} from "react-icons/fa";

function KnowledgeStats({
    statistics,
    loading,
}) {

    if (loading) {

        return (
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 h-full animate-pulse" />
        );

    }

    const cards = [

        {
            title: "Knowledge Entries",
            value:
                statistics?.knowledge_base_entries ?? 0,
            icon: (
                <FaDatabase className="text-blue-400 text-3xl" />
            ),
        },

        {
            title: "Critical",
            value:
                statistics?.critical_vulnerabilities ??
                0,
            icon: (
                <FaBug className="text-red-400 text-3xl" />
            ),
        },

        {
            title: "Reports",
            value:
                statistics?.reports_generated ?? 0,
            icon: (
                <FaShieldAlt className="text-green-400 text-3xl" />
            ),
        },

        {
            title: "AI Engine",
            value: "Online",
            icon: (
                <FaRobot className="text-purple-400 text-3xl" />
            ),
        },

    ];

    return (

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">

            <h2 className="text-xl font-semibold mb-6">
                Knowledge Base
            </h2>

            <div className="grid grid-cols-2 gap-4">

                {cards.map((item) => (

                    <div
                        key={item.title}
                        className="bg-slate-900 rounded-lg border border-slate-700 p-4"
                    >

                        <div className="flex justify-between items-center">

                            <div>

                                <p className="text-slate-400 text-sm">
                                    {item.title}
                                </p>

                                <h3 className="text-2xl font-bold mt-2">
                                    {item.value}
                                </h3>

                            </div>

                            {item.icon}

                        </div>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default KnowledgeStats;