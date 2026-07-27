import {
    FaDatabase,
    FaRobot,
    FaServer,
    FaCheckCircle,
} from "react-icons/fa";

const services = [
    {
        name: "Backend API",
        status: "Online",
        icon: <FaServer className="text-blue-400" />,
    },
    {
        name: "MongoDB",
        status: "Connected",
        icon: <FaDatabase className="text-green-400" />,
    },
    {
        name: "AI Engine",
        status: "Running",
        icon: <FaRobot className="text-purple-400" />,
    },
    {
        name: "Knowledge Base",
        status: "Synced",
        icon: <FaCheckCircle className="text-emerald-400" />,
    },
];

function SystemHealth() {
    return (
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">

            <h2 className="text-xl font-semibold mb-6">
                System Health
            </h2>

            <div className="space-y-4">

                {services.map((service) => (

                    <div
                        key={service.name}
                        className="flex justify-between items-center bg-slate-900 rounded-lg p-4 border border-slate-700"
                    >

                        <div className="flex items-center gap-3">

                            {service.icon}

                            <span>
                                {service.name}
                            </span>

                        </div>

                        <span className="text-green-400 font-semibold">
                            ● {service.status}
                        </span>

                    </div>

                ))}

            </div>

        </div>
    );
}

export default SystemHealth;