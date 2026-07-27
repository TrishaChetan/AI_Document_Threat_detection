import { NavLink } from "react-router-dom";
import {
    FaChartPie,
    FaUpload,
    FaFileAlt,
    FaHistory,
    FaBook,
    FaCog,
} from "react-icons/fa";

const links = [
    {
        name: "Dashboard",
        path: "/dashboard",
        icon: <FaChartPie />,
    },
    {
        name: "Upload Scan",
        path: "/upload",
        icon: <FaUpload />,
    },
    {
        name: "Results",
        path: "/results",
        icon: <FaFileAlt />,
    },

];

function Sidebar() {
    return (
        <aside className="w-64 bg-slate-900 border-r border-slate-800">
            <div className="p-6">
                <h2 className="text-2xl font-bold text-green-400">
                    SECURITY AI
                </h2>
            </div>

            <nav className="flex flex-col gap-2 px-3">
                {links.map((link) => (
                    <NavLink
                        key={link.path}
                        to={link.path}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                                isActive
                                    ? "bg-green-600 text-white"
                                    : "hover:bg-slate-800 text-slate-300"
                            }`
                        }
                    >
                        {link.icon}
                        {link.name}
                    </NavLink>
                ))}
            </nav>
        </aside>
    );
}

export default Sidebar;
