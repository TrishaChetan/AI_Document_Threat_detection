function SummaryCard({ title, value }) {
    return (
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-5">
            <p className="text-slate-400">
                {title}
            </p>

            <h2 className="text-3xl font-bold mt-3">
                {value}
            </h2>
        </div>
    );
}

export default SummaryCard;