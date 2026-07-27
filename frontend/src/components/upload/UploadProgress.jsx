function UploadProgress({ loading }) {

    if (!loading) return null;

    return (
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">

            <h2 className="text-xl font-semibold mb-6">
                AI Analysis Running...
            </h2>

            <div className="space-y-4">

                <p>✅ Parsing XML Scan</p>

                <p>✅ Detecting Vulnerabilities</p>

                <p>✅ AI Recommendation Engine</p>

                <p>✅ Risk Assessment</p>

                <p>✅ PDF Report Generation</p>

            </div>

        </div>
    );
}

export default UploadProgress;