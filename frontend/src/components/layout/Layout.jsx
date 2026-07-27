import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

function Layout({ children }) {
    return (
        <div className="flex min-h-screen bg-slate-950 text-white">
            <Sidebar />

            <div className="flex flex-col flex-1">
                <Navbar />

                <main className="flex-1 p-6 overflow-auto">
                    {children}
                </main>
            </div>
        </div>
    );
}

export default Layout;