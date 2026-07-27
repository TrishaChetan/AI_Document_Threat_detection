import { FaShieldAlt } from "react-icons/fa";

function Navbar() {
    return (
        <header className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6">
            <div>
                <h1 className="text-xl font-bold flex items-center gap-2">
                    <FaShieldAlt className="text-green-500" />
                    Guardex AI
                </h1>

                <p className="text-sm text-slate-400">
                    AI Powered Web Vulnerability Assessment Platform
                </p>
            </div>

            <div className="text-right">
                <p className="font-semibold">System Status</p>

                <span className="text-green-400 text-sm">
                    ● Online
                </span>
            </div>
        </header>
    );
}

export default Navbar;