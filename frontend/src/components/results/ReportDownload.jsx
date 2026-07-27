function ReportDownload({ report }) {
    return (
        <a
            href={`http://127.0.0.1:8000${report.download_url}`}
            target="_blank"
            rel="noreferrer"
            className="inline-block bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
        >
            Download PDF Report
        </a>
    );
}

export default ReportDownload;