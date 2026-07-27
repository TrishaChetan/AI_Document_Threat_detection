function StatsCard({
    title,
    value,
    subtitle,
    icon,
    color = "bg-slate-800",
    loading = false,
}) {
    return (
        <div
            className={`${color} rounded-xl p-6 border border-slate-700 shadow-lg hover:shadow-2xl hover:-translate-y-1 transition duration-300`}
        >
            {loading ? (
                <div className="animate-pulse space-y-3">
                    <div className="h-4 bg-slate-600 rounded w-1/2"></div>
                    <div className="h-8 bg-slate-600 rounded w-1/3"></div>
                    <div className="h-3 bg-slate-700 rounded w-2/3"></div>
                </div>
            ) : (
                <div className="flex justify-between items-center">
                    <div>
                        <p className="text-slate-400 text-sm">
                            {title}
                        </p>

                        <h2 className="text-4xl font-bold mt-2">
                            {value}
                        </h2>

                        <p className="text-xs text-slate-400 mt-3">
                            {subtitle}
                        </p>
                    </div>

                    <div className="text-5xl">
                        {icon}
                    </div>
                </div>
            )}
        </div>
    );
}

export default StatsCard;