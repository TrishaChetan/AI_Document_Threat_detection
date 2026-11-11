import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import UploadBox from "../components/upload/UploadBox";
import UploadProgress from "../components/upload/UploadProgress";
import { uploadScan } from "../services/scanService";

function Upload() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleUpload = async () => {
        if (!file) {
            toast.error("Please select a ZAP .xml or .json report.");
            return;
        }

        try {
            setLoading(true);

            const result = await uploadScan(file);

            console.log("Backend Response:", result);

            toast.success("Scan completed successfully!");

            navigate("/results", {
                state: {
                    result,
                },
            });

        } catch (err) {
            console.error(err);

            toast.error(err.detail || "Upload failed.");

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8">

            <div>
                <h1 className="text-4xl font-bold">
                    Upload Security Scan
                </h1>

                <p className="text-slate-400 mt-2">
                    Upload an OWASP ZAP report (XML or JSON) for AI-powered analysis.
                </p>
            </div>

            <UploadBox
                file={file}
                setFile={setFile}
            />

            <button
                onClick={handleUpload}
                className="bg-green-600 hover:bg-green-700 px-8 py-4 rounded-lg font-semibold transition"
            >
                {loading ? "Analyzing..." : "Upload & Analyze"}
            </button>

            <UploadProgress
                loading={loading}
            />

        </div>
    );
}

export default Upload;